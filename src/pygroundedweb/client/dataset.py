import logging
import mimetypes
import os
import time
from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Callable

from .exception import APIError, UploadError, NetworkError, PermissionDenied
from ..models.dataset import Dataset
from .base import APIModelClient

logger = logging.getLogger(__name__)

class DatasetClient(APIModelClient):

    def _parse_json(self, dataset_json: dict) -> Dataset:
        if "mutable_fields" not in dataset_json and "immutable_fields" not in dataset_json:
            dataset_json["mutable_fields"] = ["name"]

        instance = Dataset.model_validate(dataset_json)
        object.__setattr__(instance, "_client", self)
        return instance

    def _create_dataset_photo(self, dataset_id: int, photo_path: str, photo_type: str):
        filename = os.path.basename(photo_path)
        size = os.path.getsize(photo_path)
        content_type, _ = mimetypes.guess_type(photo_path)
        content_type = content_type or 'application/octet-stream'

        payload = {
            "type": photo_type,
            "file_data": {
                "filename": filename,
                "content_type": content_type,
                "size": size
            },
            "dataset_id": dataset_id
        }
        data = self._client.create("datasetphotos", payload)

        upload_req = data.get("upload_request")
        photo_id = data.get("pk") or data.get("id")
        if not upload_req or not photo_id:
            raise ValueError(f"[{filename}] upload_request ou photo_id manquant")

        return upload_req["url"], upload_req.get("fields", {}), photo_id

    def _upload_photo(self, url: str, fields: dict, photo_path: str, content_type: str) -> bool:
        filename = os.path.basename(photo_path)
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            try:
                with open(photo_path, 'rb') as f:
                    files = {'file': (filename, f, content_type)}
                    r = self._client.session.post(url, data=fields, files=files)
                    r.raise_for_status()
                return True
            except Exception as e:
                logging.warning(f"[{filename}] Upload tentative {attempt} échouée : {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)

        logging.error(f"[{filename}] Échec complet de l'upload après {max_retries} tentatives.")
        return False

    def _confirm_photo(self, photo_id: int) -> bool:
        try:
            rc = self._client.post(f"datasetphotos/{photo_id}/confirm-upload/")
            rc.raise_for_status()
            return True
        except Exception as e:
            logging.error(f"[{photo_id}] Échec de la confirmation de la photo : {e}")
            return False

    def _process_photo(self, dataset_id: int, photo_path: str, photo_type: str) -> bool:
        filename = os.path.basename(photo_path)

        try:
            url, fields, photo_id = self._create_dataset_photo(dataset_id, photo_path, photo_type)
        except Exception as e:
            logging.error(f"[{filename}] Échec création ressource : {e}")
            return False

        content_type, _ = mimetypes.guess_type(photo_path)
        content_type = content_type or 'application/octet-stream'

        if not self._upload_photo(url, fields, photo_path, content_type):
            return False

        return self._confirm_photo(photo_id)

    def _prepare_and_validate_tasks(self, photos_before: List[str], photos_after: List[str]) -> List[tuple]:
        p_before = photos_before or []
        p_after = photos_after or []

        if not p_before and not p_after:
            raise ValueError("Impossible de créer un dataset vide.")

        tasks = [(str(p), "before") for p in p_before] + \
                [(str(p), "after") for p in p_after]

        for path, _ in tasks:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Le fichier {path} est introuvable.")

        return tasks

    def _initialize_dataset(self, dataset_name: str) -> int:
        ds_data = self._client.create("datasets/", {"name": dataset_name})
        dataset_id = ds_data.get("pk") or ds_data.get("id")

        if not dataset_id:
            raise APIError("Création réussie côté serveur, mais ID manquant dans la réponse JSON.")

        logger.info(f"Dataset initialisé (ID: {dataset_id})")
        return dataset_id

    def _upload_photos_concurrently(
            self,
            dataset_id: int,
            tasks: List[tuple],
            max_workers: int,
            progress_callback: Optional[Callable[[int, int], None]]
    ) -> None:
        total_files = len(tasks)
        successful_uploads = 0
        failed_uploads = 0

        def update_progress(current: int):
            if progress_callback:
                try:
                    progress_callback(current, total_files)
                except Exception:
                    pass

        update_progress(0)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(self._process_photo, dataset_id, path, p_type): path
                for path, p_type in tasks
            }

            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    if future.result():
                        successful_uploads += 1
                    else:
                        failed_uploads += 1
                except Exception as e:
                    logger.error(f"Exception non gérée lors de l'upload de {path}: {e}")
                    failed_uploads += 1

                update_progress(successful_uploads + failed_uploads)

        if failed_uploads > 0:
            raise UploadError(
                f"L'upload a échoué pour {failed_uploads} fichiers sur {total_files}. "
                "Le dataset n'a pas été confirmé."
            )

    def _confirm_and_retrieve(self, dataset_id: int) -> Dataset:
        self._client.post(f"datasets/{dataset_id}/confirm-upload/")
        logger.info("Dataset confirmé sur le serveur.")

        final_resp = self._client.get(f"datasets/{dataset_id}/")
        return self._parse_json(final_resp.json())

    def create(
            self,
            dataset_name: str,
            photos_before: List[str] = None,
            photos_after: List[str] = None,
            max_workers: int = 5,
            progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dataset:
        tasks = self._prepare_and_validate_tasks(photos_before, photos_after)
        dataset_id = self._initialize_dataset(dataset_name)
        self._upload_photos_concurrently(dataset_id, tasks, max_workers, progress_callback)
        return self._confirm_and_retrieve(dataset_id)

    def retrieve(self, dataset_id: int):
        dataset_json = self._client.get_by_id("datasets", dataset_id)
        return self._parse_json(dataset_json)

    def update(self, dataset: Dataset):
        dataset_json = self._client.update("datasets", dataset)
        return self._parse_json(dataset_json)

    def delete(self, dataset_id: int):
        self._client.delete_by_id("datasets", dataset_id)