from setuptools import setup

requirements = [
    # TODO: put your package requirements here
]

setup(
    name='routing_simulation',
    version='0.0.1',
    description="Simulacion en envío de paquetes por ruta más corta",
    author="routing_simulation",
    author_email='alessandrojcuppari@gmail.com',
    url='https://github.com/alessandrojcm/routing_simulation',
    packages=['routing_simulation', 'routing_simulation.images',
              'routing_simulation.tests'],
    package_data={'routing_simulation.images': ['*.png']},
    entry_points={
        'console_scripts': [
            'Simulador de encaminamiento=routing_simulation.routing_simulator:main'
        ]
    },
    install_requires=requirements,
    zip_safe=False,
    keywords='routing_simulation',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
