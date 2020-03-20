# CSI4900-Phishing-Website-Detection

## Requirements

- Python 3.6+
- Windows 10
- Powershell
- Docker

## How to set up

### Docker Set up fow Windows 10

Follow the instructions found in this website: https://www.sitepoint.com/docker-windows-10-home/. (You can skip the part with the node application at the end)

### Install the Docker Containers needed to run the scripts

Start your Docker VM: `docker-machine start <name of your docker vm>`

Run the following command:

```
docker-machine env --shell cmd <name of your docker vm>
@FOR /f "tokens=*" %i IN ('docker-machine env --shell cmd <name of your docker vm>') DO @%i
```

This will ensure Docker will run on Windows

#### Get the DNSTwist Docker Container

Pull the dnstwist container using this command while docker vm is running: `docker pull elceef/dnstwist`

#### Get the httprobe Docker Container

Clone the httprobe repo: `git clone https://github.com/tomnomnom/httprobe.git`

cd into the cloned httprobe repo

Build the httprobe container using this command while docker vm is running: `docker build -t httprobe .`

### Running the scripts

0. Ensure you are in the project directory and you have the Docker machine set up and currently running
1. Install all the required packages by typing 'pip install -r requirements.txt'. This recursively reads the contents of requirements.txt and installs each package per line
1. (Optional) - In the config.json file, if you have a censys.io account, feel free to include your api and secret key in the fields provided

```
{
    "censys_UID": "<Your API key>",
    "censys_Secret": "<Your Secret Key>"
}
```

3. Now you can run the main.py script, which will carry out the steps currently implemented in the phishing website detection loop. Do so by calling the script as followed: `python main.py <full url of legitiment site that can be targeted by phishing>` (python main.py https://www.bell.ca/)

To Run MLEvlauation: python src\MLEvaluation\build_features.py https://www.paypal.com/ca/signin paypal phishing_sites\paypal.txt phishing_sites\legit_urls.txt
