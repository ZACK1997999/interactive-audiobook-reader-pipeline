from setuptools import setup


setup(
    name="immersive-audiobook-reader-pipeline",
    version="0.5.0",
    description="A configurable EPUB/audiobook alignment and immersive reader pipeline",
    py_modules=[
        "acoustic_whisper",
        "models",
        "audio_resolver",
        "alignment_backend",
        "contract_adapters",
        "chapter_resolver",
        "chapter_locator",
        "chapter_metadata",
        "acoustic_backend",
        "whisperx_backend",
        "config",
        "dynamic_aligner",
        "extract_epub",
        "html_builder",
        "pipeline",
        "run_manifest",
        "validate_outputs",
        "manifests",
        "publication_verify",
        "r2_upload",
        "quality_gate",
        "industrial_orchestrator",
        "agy_linguistic_worker",
        "mlx_acoustic_worker",
        "intake_reconciler",
        "publisher",
    ],
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "acoustic": ["mlx-whisper"], "whisperx": ["whisperx"],
        "deployment": ["boto3>=1.34", "Pillow>=10"],
    },
    entry_points={
        "console_scripts": [
            "reader-pipeline=pipeline:main",
            "reader-validate=validate_outputs:main",
            "reader-r2-upload=r2_upload:main",
            "reader-quality-check=quality_gate:main",
            "reader-intake=intake_reconciler:main",
            "reader-publish=publisher:main",
        ]
    },
)
