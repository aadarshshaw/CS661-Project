# Unveiling Earth’s Climate Odyssey

## A Comprehensive Data Analysis of Global Warming and Climate Change

## Cs661 Project - Group 9

## Running Via Python

1. Install the necessary packages in the requirements.txt file.
2. Run the project using the following command:

```
python app.py
```

## Running from Dockerfile

First build the image from the dockerfile using the following command while in the root directory of the project:

```
docker build -t cs661-proj .
```

Then run the image using the following command:

```
docker run --rm -itd -p 5000:5000 cs661-proj
```

The server will be running on port 5000. To access the server, open a web browser and navigate to `http://localhost:5000/`.

## Team Members

- Aadarsh Shaw
- Abhishek Rajwanshi
- Aishwarya Srivastava
- Ankit Choudhary
- Harsh Chaudhary
- Niharika Khatri
- Sejal Sahu
- Shamayeeta Dass
