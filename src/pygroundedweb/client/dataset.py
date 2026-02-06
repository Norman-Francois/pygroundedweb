import logging
import mimetypes
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List

from ..models.dataset import Dataset
from .base import APIModelClient


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
        resp = self._client.post("/datasetphotos/", json=payload)
        resp.raise_for_status()
        data = resp.json()

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
                time.sleep(2 ** attempt)

        logging.error(f"[{filename}] Échec complet de l'upload après {max_retries} tentatives.")
        return False

    def _confirm_photo(self, photo_id: int) -> bool:
        try:
            rc = self._client.post(f"/datasetphotos/{photo_id}/confirm-upload/")
            rc.raise_for_status()
            return True
        except Exception as e:
            logging.error(f"[{photo_id}] Échec de la confirmation de la photo : {e}")
            return False

    def _process_photo(self, dataset_id: int, photo_path: str, photo_type: str) -> bool:
        filename = os.path.basename(photo_path)

        # 1) création
        try:
            url, fields, photo_id = self._create_dataset_photo(dataset_id, photo_path, photo_type)
        except Exception as e:
            logging.error(f"[{filename}] Échec création ressource : {e}")
            return False

        # type MIME
        content_type, _ = mimetypes.guess_type(photo_path)
        content_type = content_type or 'application/octet-stream'

        # 2) upload
        if not self._upload_photo(url, fields, photo_path, content_type):
            return False

        # 3) confirmation
        return self._confirm_photo(photo_id)

    def create(
            self,
            dataset_name: str,
            photos_before_paths: list[str] = None,
            photos_after_paths: list[str] = None,
            photos_before_dir: str = None,
            photos_after_dir: str = None,
            max_workers: int = 5
    ) -> bool:
        try:
            # 1) Création du dataset
            resp = self._client.post("/datasets/", json={"name": dataset_name})
            resp.raise_for_status()
            ds = resp.json()
            dataset_id = ds.get("pk") or ds.get("id")
            if not dataset_id:
                logging.error("ID du dataset manquant dans la réponse.")
                return False
            logging.info(f"Dataset créé (ID: {dataset_id})")

            # 2) Collecte des chemins de photos
            photos_before = photos_before_paths or []
            photos_after = photos_after_paths or []

            photos_before += _get_photos_from_dir(photos_before_dir)
            photos_after += _get_photos_from_dir(photos_after_dir)

            photos = []
            for path in photos_before:
                photos.append((path, "before"))
            for path in photos_after:
                photos.append((path, "after"))

            # 3) Traitement parallèle de chaque photo
            futures = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for path, photo_type in photos:
                    if not os.path.isfile(path):
                        logging.warning(f"Fichier introuvable, skip : {path}")
                        continue
                    futures.append(
                        executor.submit(self._process_photo, dataset_id, path, photo_type)
                    )

            # collecte des résultats
            success = sum(1 for f in futures if f.result())
            total = len(futures)
            logging.info(f"{success}/{total} photos traitées avec succès.")
            if success != total:
                logging.error(f"{total - success} photo(s) ont échoué.")
                return False

            conf = self._client.post(f"/datasets/{dataset_id}/confirm-upload/")
            conf.raise_for_status()
            logging.info("Upload du dataset confirmé.")
            return True

        except Exception as e:
            logging.error(f"Erreur dans create: {e}")
            return False

    def retrieve(self, dataset_id: int):
        dataset_json = self._client.get_by_id("datasets", dataset_id)
        return self._parse_json(dataset_json)

    def update(self, dataset: Dataset):
        dataset_json = self._client.update("datasets", dataset)
        return self._parse_json(dataset_json)

    def delete(self, dataset_id: int):
        self._client.delete_by_id("datasets", dataset_id)


def _get_photos_from_dir(directory: str) -> list[str]:
    """
    Retourne les chemins absolus des fichiers valides dans un dossier.
    """
    if not directory or not os.path.isdir(directory):
        logging.warning(f"Dossier invalide ou non précisé : {directory}")
        return []
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]