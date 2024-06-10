from setuptools import setup, find_packages

setup(
    name='youtubedl-web',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'yt-dlp',
        'flask_socketio',
        'flask_session'
    ],
    entry_points={
        'console_scripts': [
            'youtubedlWeb=youtubedlWeb.youtubedl:main',
        ],
    },
    author='Bartosz Brzozowski',
    author_email='bartosz.brzozowski23@gmail.com',
    description='Youtubedl web',
    url='https://github.com/bartek56/youtubedl-web',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
