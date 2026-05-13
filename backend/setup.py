"""
Setup configuration for DITA Backend
"""

from setuptools import setup, find_packages

setup(
    name="dita-backend",
    version="2.0.0",
    description="Dieng Intelligence Tourism Assistant - AI Backend",
    author="Tim PJK-GM067",
    author_email="",
    packages=find_packages(),
    python_requires=">=3.13",
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "python-dotenv>=1.0.0",
        "requests>=2.32.0",
        "pandas>=2.2.0",
        "numpy>=2.0.0",
        "scikit-learn>=1.5.0",
        "google-generativeai>=0.8.0",
        "websockets>=13.0",
    ],
    extras_require={
        "dev": [
            "jupyter>=1.0.0",
            "matplotlib>=3.9.0",
            "seaborn>=0.13.0",
            "ipykernel>=6.29.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.13",
    ],
)
