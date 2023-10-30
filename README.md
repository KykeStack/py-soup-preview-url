# link-preview-generator

The python version of URL preview on Node.js repo

## About

🌐🔍 This Repo facilitates the creation of URL previews by scraping information from a specified web page. 

It leverages the Playwright library for web automation and includes custom functions from separate modules to extract a variety of details from the provided URL, such as the domain name, image preview URL, favicon, title, and description. 🚀

## Install

```
$ pip install -r requirements.txt 
  playwright install chromium
```

### Start Local
```
$ uvicorn main:app --host 0.0.0.0 --port 10000

```
## Environment Variables:


🔐 JWT_SECRET_KEY (openssl rand -hex 32)
This environment variable is meant to store a secret key for JSON Web Token (JWT) authentication or encryption.

🚫 RESOURCE_EXCLUSIONS (Array: ["image", "stylesheet", "media"])
RESOURCE_EXCLUSIONS is an array that specifies the types of web resources to exclude when making requests to a web page.

See also the example.env 🔍

## Usage

### Using the CMD with Curl 
```bash
curl --location 'http://localhost:8086/preview/?url=https%3A%2F%2Fwww.freecodecamp.org%2Flearn' \
--header 'Authorization: Bearer {your_access_token}'
```

### Or javascript 
  ```js
    const myHeaders = new Headers();
    myHeaders.append("Authorization", "Bearer {your_access_token}");

    const requestOptions = {
      method: 'GET',
      headers: myHeaders,
      redirect: 'follow'
    };

    fetch("http://localhost:8086/preview/?url=https://www.freecodecamp.org/learn", requestOptions)
      .then(response => response.text())
      .then(result => console.log(result))
      .catch(error => console.log('error', error));
  ```


## You can also run it with Docker 

Execute the command in the root directory
 ``` bash
  docker compose -f compose.yaml up
  ```

Or from script 
 ``` bash
  ./run-docker-compose.sh 
  ```

## API

### findURLPreview(url)

Accepts a `url`, which is scraped and Returns an object with preview data of `url`.

#### url

Type: `string`

Scraped url.


## How it works

The primary function is, "findURLPreview(urlLink)," takes a URL as input and performs the following actions:

Launches a headless Chromium browser for web page interaction.

Navigates to the specified URL.

Excludes specific web resources, as defined in the RESOURCE_EXCLUSIONS environment variable, by aborting their requests.

Retrieves essential information from the web page, such as the domain name, image preview URL, favicon, title, description, and the final URL (in case of redirection).

Closes the browser session to conserve resources.

Returns an object containing the extracted information, including domain, image, favicon, title, description, and URL.


