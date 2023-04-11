# Group Information

* Naveen Kumar Golla <naveeng@csu.fullerton.edu> 885185843
* Lakshmi Manasa Pothakamuru  <Manasapothakamuru@csu.fullerton.edu> 885214536
* Sai Chand Meda <medasai@csu.fullerton.edu> 885237370

# Flask Project Setup

**Recipe blog**: Public can visit the site and look after lastest recipes posted by admin team.   

## Setup

1. Clone this repository to your local machine:

```bash
git clone https://github.com/Naveen-Golla123/CPSC-449_Mid-Project.git
```

2. Create a virtual environment for the project:

```bash
python3 -m venv venv
```

3. Activate the virtual environment:

```bash
venv/bin/activate
```

4. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

To start the application, run the following command:

```bash
python app.py
```

This will start the application on `http://localhost:5000`.

## Project Structure

The project is structured as follows:



## Features

- Register and login APIs for admin team.
- API for creating a recipe, with desciption, headline and post ( this is private API ).
- API for getting a recipe by given recipeID. 
- API for getting allRecipes in one fetch.
- API for fetcing uploaded file by fileName, which was given while creating recipe. 

## Screenshots

![App Screenshot]()

