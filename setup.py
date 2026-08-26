from setuptools import setup


setup(
    name="immersive-audiobook-reader-pipeline",
    version="0.4.0",
    description="A configurable EPUB/audiobook alignment and immersive reader pipeline",
    py_modules=[
        "acoustic_whisper",
        "models",
        "audio_resolver",
        "config",
        "dynamic_aligner",
        "extract_epub",
        "html_builder",
        "pipeline",
        "run_manifest",
        "validate_outputs",
    ],
    python_requires=">=3.9",
    install_requires=[],
    extras_require={"acoustic": ["mlx-whisper"]},
    entry_points={
        "console_scripts": [
            "reader-pipeline=pipeline:main",
            "reader-validate=validate_outputs:main",
        ]
    },
)
