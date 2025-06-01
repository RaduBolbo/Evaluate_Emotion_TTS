# Steps to run the application:

1) Run the following commands in bash (Linux) or in Anaconda prompt (Windows):

`conda create -n subjective_eval python=3.10`

`conda activate subjective_eval `

`pip install -r requirements.txt`

Or jus run `pip install pygame==2.1.0`, then `pip install gdown`

2) Downlaod the resources:

Option 1:

`python download_resources.py`

Option 2:

Or download manualy the archive from https://drive.google.com/file/d/14rccGeMWVnuudF7UjZHa7lYcwrr8dl3c/view?usp=sharing, unzip it and then make sure the data directory is in project's root directory

3) Then, run the 5 applications, one after another:

python app_part1_naturalness.py
python app_part2_EDT.py
python app_part3_EIT.py
python app_part4_EST.py
python app_part5_EDiT.py

4) Finally, send the contents of the `results` folder to radu.bolborici@gmail.com.