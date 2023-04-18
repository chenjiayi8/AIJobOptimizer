# AIJobOptimizer

AIJobOptimizer: Revolutionize your job application process with AI-driven resume and motivation letter enhancements, designed to capture employers' attention and increase your success in the job market.

## Setup

### How to install virtualenv

#### Install pip first

```
sudo apt-get install python3-pip
```

#### Then install virtualenv using pip3

```
sudo pip3 install virtualenv
```

### Setup the project

#### Clone the repository and navigate to the project directory

```
git@github.com:chenjiayi8/AIJobOptimizer.git

cd AIJobOptimizer
```

#### Create a new virtual environment

```
virtualenv --python=python3.10 env
source env/bin/activate
```

#### Install dependencies from requirements.txt

```
pip install -r requirements.txt
```

#### Create a copy of the .env.example file and name it .env:

```
cp .env.example .env
```

#### Running the Application

```
streamlit run app.py --server.port 8080

The web server should now be running at http://127.0.0.1:8080/.
```
