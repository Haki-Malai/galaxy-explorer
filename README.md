# galaxy-explorer
Galaxy Explorer is a python program for searching Star Wars API, featuring caching and visualization of past search results. This command line interface allows you to search for characters in the Star Wars API and generate fake searches. You can also view the application logs by plotting the results or time. Additionally, you can print the cache and clear it if desired.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/Haki-Malai/galaxy-explorer.git
```
2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage
### Search for a character
To search for a character, use the search command:
```python
python main.py search "Luke Skywalker"
```
You can also choose to print the character's home world or raise errors and warnings:
```bash
python main.py search "Leia Organa" --world --verbose
```

### Generate fake searches
To generate fake searches, use the fake command and specify the number of searches to generate:
```python
python main.py fake 10
```

### View application logs
To view the application logs, use the plot command and specify whether to visualize the results or time:
```bash
python main.py plot
python main.py plot --results
python main.py plot --time
```

### Clear the cache
To clear the cache, use the cache command:
```bash
python main.py cache --clean
```

### Test the application
To test the application, use the test command:
```bash
python main.py test # or:
python main.py test --coverage
```

### Help
To view the help message and available options for a command, use the --help option:
```bash
python main.py search --help
```

### Licence
This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details.