import setuptools

setuptools.setup(
    name="agentic_sports",
    version="0.1.0",
    author="Agentic Sports Community",
    description="A reusable simulator engine for LLM-powered sports agents.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=[
        "google-genai>=1.0.0",
    ],
)
