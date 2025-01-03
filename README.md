# SciELO Log Validator

The SciELO Log Validator project provides tools to validate log files for the SciELO platform. It includes both command line and Python library usage options.


## Installation

To install the SciELO Log Validator, you can use `pip`:

```bash
pip install scielo-log-validator
```

Alternatively, you can clone the repository and install the dependencies manually:

```bash
git clone https://github.com/scieloorg/scielo_log_validator.git
cd scielo_log_validator
pip install -r requirements.txt
```

## To set up a development environment, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/scieloorg/scielo_log_validator.git
cd scielo_log_validator
  ```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in editable mode:
```bash
pip install -e .
```

5. Run tests to ensure everything is set up correctly:
```bash
python -m unittest discover
```


## Usage

__Command line__

```bash
usage: log_validator [-h] -p PATH [-s SAMPLE_SIZE] [--apply_path_validation] [--apply_content_validation]

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  File or directory to be checked
  -s SAMPLE_SIZE, --sample_size SAMPLE_SIZE
              Sample size to be checked (must be between 0 and 1)
  --apply_path_validation
                        Indicates whether to apply path validation
  --apply_content_validation
                        Indicates whether to apply content validation

# Here is an example of execution for a single file:
log_validator -p /home/user/2022-03-01_scielo-br.log.gz --apply_path_validation --apply_content_validation

# Here is an example of execution for an entire directory:
log_validator -p /home/user --apply_path_validation --apply_content_validation
```

__Python library__

```python
from scielo_log_validator import validator

# Validate a single file
result = validator.pipeline_validate('/home/user/2022-03-01_scielo-br.log.gz', sample_size=1000, apply_path_validation=True, apply_content_validation=True)

# Validate all files in a directory
for root, _, files in os.walk('/home/user'):
    for file in files:
        file_path = os.path.join(root, file)
        results = validator.pipeline_validate(
            file_path, 
            0.1,
            apply_path_validation=True,
            apply_content_validation=True
        )
```

__Result format__

In both modes, the output of the validation process is a JSON object that provides detailed information about the log file, including a summary of the content, validation status, and path details. Here is an example of the output:

```json
{
  "/home/user/2022-03-01_scielo-br.log.gz": {
    "content": {
      "summary": {
        "datetimes": {
          "(2022, 3, 1, 23)": 5,
          "(2022, 3, 2, 0)": 312,
          "(2022, 3, 2, 1)": 319,
          "(2022, 3, 2, 2)": 321,
          "(2022, 3, 2, 3)": 331,
          "(2022, 3, 2, 4)": 321,
          "(2022, 3, 2, 5)": 320,
          "(2022, 3, 2, 6)": 324,
          "(2022, 3, 2, 7)": 376,
          "(2022, 3, 2, 8)": 345,
          "(2022, 3, 2, 9)": 480,
          "(2022, 3, 2, 10)": 416,
          "(2022, 3, 2, 11)": 506,
          "(2022, 3, 2, 12)": 620,
          "(2022, 3, 2, 13)": 452,
          "(2022, 3, 2, 14)": 419,
          "(2022, 3, 2, 15)": 399,
          "(2022, 3, 2, 16)": 518,
          "(2022, 3, 2, 17)": 419,
          "(2022, 3, 2, 18)": 406,
          "(2022, 3, 2, 19)": 615,
          "(2022, 3, 2, 20)": 668,
          "(2022, 3, 2, 21)": 546,
          "(2022, 3, 2, 22)": 683,
          "(2022, 3, 2, 23)": 442
        },
        "invalid_lines": 0,
        "ips": {
          "local": 324,
          "remote": 10239
        },
        "total_lines": 105634
      }
    },
    "is_valid": {
      "all": true,
      "dates": true,
      "ips": true
    },
    "path": {
      "collection": null,
      "date": "2022-03-01",
      "extension": ".gz",
      "mimetype": "application/gzip",
      "paperboy": false
    },
  "probably_date": datetime.datetime(2022, 3, 2, 0, 0)}
}
```