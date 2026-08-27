from __future__ import annotations

import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from django.conf import settings
from django.utils import timezone


class DiagnosticInferenceError(RuntimeError):
    """Erro controlado ao carregar ou executar o classificador de imagens."""


class KerasImageClassifier:
    """Carrega um modelo Keras sob demanda e classifica imagens enviadas."""

    def __init__(self, model_path: str | Path | None = None, labels_path: str | Path | None = None):
        self.model_path = Path(model_path) if model_path else None
        self.labels_path = Path(labels_path) if labels_path else None
        self._model: Any = None
        self._labels: list[str] | None = None

    @property
    def models_directories(self) -> tuple[Path, ...]:
        core_directory = Path(settings.BASE_DIR) / 'core'
        return (
            core_directory / 'cnn_model',
            core_directory / 'cnn_models',
        )

    def _find_model(self) -> Path:
        if self.model_path:
            path = self.model_path
            if not path.is_absolute():
                path = Path(settings.BASE_DIR) / path
            if path.is_file():
                return path
            raise DiagnosticInferenceError(f'Modelo Keras não encontrado: {path}')

        candidates = []
        for directory in self.models_directories:
            candidates.extend(directory.rglob('*.keras'))
            candidates.extend(directory.rglob('*.h5'))
            candidates.extend(directory.rglob('*.hdf5'))
        candidates.sort()
        if not candidates:
            raise DiagnosticInferenceError(
                'Nenhum modelo Keras encontrado em core/cnn_model ou core/cnn_models.'
            )
        return candidates[0]

    def _load_labels(self, model_path: Path) -> list[str] | None:
        path = self.labels_path or model_path.with_suffix('.json')
        if not path.is_absolute():
            path = Path(settings.BASE_DIR) / path
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            raise DiagnosticInferenceError(f'Arquivo de classes inválido: {path}') from exc
        if not isinstance(data, list) or not all(isinstance(label, str) for label in data):
            raise DiagnosticInferenceError('O arquivo de classes deve conter uma lista de textos.')
        return data

    def load(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from tensorflow.keras.models import load_model
        except ImportError as exc:
            raise DiagnosticInferenceError(
                'TensorFlow não está instalado. Instale a dependência para executar a inferência.'
            ) from exc
        model_path = self._find_model()
        try:
            self._model = load_model(model_path, compile=False)
        except Exception as exc:
            raise DiagnosticInferenceError(f'Não foi possível carregar o modelo: {model_path}') from exc
        self._labels = self._load_labels(model_path)
        return self._model

    def predict(self, image_file: Any) -> dict[str, Any]:
        model = self.load()
        try:
            import numpy as np
            from PIL import Image

            image = Image.open(image_file).convert('RGB')
            input_shape = model.input_shape
            height = input_shape[1] or 224
            width = input_shape[2] or 224
            batch = np.asarray(image.resize((width, height)), dtype='float32') / 255.0
            prediction = np.asarray(model.predict(np.expand_dims(batch, axis=0), verbose=0)).reshape(-1)
        except (ImportError, OSError, TypeError, ValueError, IndexError) as exc:
            raise DiagnosticInferenceError('A imagem não pôde ser processada pelo modelo.') from exc

        if prediction.size == 0:
            raise DiagnosticInferenceError('O modelo não retornou uma previsão.')
        if prediction.size == 1:
            confidence = float(prediction[0])
            index = int(confidence >= 0.5)
            scores = [1.0 - confidence, confidence]
        else:
            scores = prediction.tolist()
            index = int(np.argmax(prediction))
            confidence = float(prediction[index])
        label = self._labels[index] if self._labels and index < len(self._labels) else f'classe_{index}'
        return {'label': label, 'confidence': round(confidence, 4), 'scores': scores}


classifier = KerasImageClassifier()

_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='diagnostico')
_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def _update_job(job_id: str, **values: Any) -> None:
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].update(values)


def _run_job(job_id: str, image_paths: list[Path]) -> None:
    results = []
    try:
        _update_job(job_id, status='processing')
        for index, image_path in enumerate(image_paths, start=1):
            with image_path.open('rb') as image_file:
                result = classifier.predict(image_file)
            results.append({'filename': image_path.name, **result})
            _update_job(job_id, processed=index, results=results.copy())
        _update_job(job_id, status='completed', processed=len(image_paths), results=results)
    except DiagnosticInferenceError as exc:
        _update_job(job_id, status='failed', error=str(exc), results=results)
    except Exception:
        _update_job(job_id, status='failed', error='Não foi possível concluir o diagnóstico.', results=results)
def submit_diagnostic(images: list[Any]) -> str:
    """Salva imagens temporárias e inicia uma inferência em segundo plano."""
    job_id = uuid.uuid4().hex
    job_directory = Path(settings.MEDIA_ROOT) / 'diagnostic_jobs' / job_id
    job_directory.mkdir(parents=True, exist_ok=False)
    image_paths = []
    try:
        for index, image in enumerate(images):
            suffix = Path(image.name).suffix.lower() or '.jpg'
            image_path = job_directory / f'image_{index}{suffix}'
            with image_path.open('wb') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            image_paths.append(image_path)
    except Exception:
        import shutil
        shutil.rmtree(job_directory, ignore_errors=True)
        raise DiagnosticInferenceError('Não foi possível preparar as imagens para análise.')

    with _jobs_lock:
        _jobs[job_id] = {
            'status': 'queued',
            'created_at': timezone.now().isoformat(),
            'total': len(image_paths),
            'processed': 0,
            'results': [],
            'error': None,
        }
    _executor.submit(_run_job, job_id, image_paths)
    return job_id


def get_diagnostic_job(job_id: str) -> dict[str, Any] | None:
    with _jobs_lock:
        job = _jobs.get(job_id)
        return job.copy() if job else None


def get_diagnostic_image_path(job_id: str, filename: str) -> Path | None:
    """Retorna uma imagem do job sem permitir escapar da pasta do diagnóstico."""
    job_directory = Path(settings.MEDIA_ROOT) / 'diagnostic_jobs' / job_id
    image_path = (job_directory / filename).resolve()
    try:
        image_path.relative_to(job_directory.resolve())
    except ValueError:
        return None
    return image_path if image_path.is_file() else None