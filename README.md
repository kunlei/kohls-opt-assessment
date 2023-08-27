# Pizza Assortment Optimization

The code in this repository aims to solve the pizza assortment optimization problem.
There are three directories:

+ `\doc`: 
  + The `Take_home_assignment_for_DecSci.pdf` contains the problem description and modeling requirements.
  + The `model.tex` contains the `LaTeX` source file for the mathematical models.
  + The `model.pdf` contains the mathematical models to solve the pizza assortment optimization problem.
+ `\src`:
  + The `opt_service.py` is the interface to the optimizer.
  + The `\common` package defines core classes for modeling purposes.
  + The `\model` package contains the two model implementations to solve the pizza assortment optimization problems.
  + The `\processor` package takes care of processing input and model output
  + The `\utils` package contains supporting functions used in other packages.
+ `\tests`:
  + The files in this directory contains unit tests for the developed optimization engine.

The expanded file structure is shown below.

```commandline
.
├── README.md
├── doc
│   ├── Take_home_assignment_for_DecSci.pdf
│   ├── model.pdf
│   └── model.tex
├── poetry.lock
├── pyproject.toml
├── src
│   ├── __init__.py
│   ├── common
│   │   ├── __init__.py
│   │   ├── data_center.py
│   │   └── store.py
│   ├── model
│   │   ├── __init__.py
│   │   ├── pizza_assortment_optimizer.py
│   │   └── pizza_assortment_optimizer_group.py
│   ├── opt_service.py
│   ├── processor
│   │   ├── __init__.py
│   │   ├── input_processor.py
│   │   └── output_processor.py
│   └── utils
│       ├── __init__.py
│       └── validator.py
└── tests
    ├── __init__.py
    ├── data
    │   └── new_pizza.csv
    ├── test_data_center.py
    ├── test_model_1.py
    ├── test_model_2.py
    └── test_store.py
```