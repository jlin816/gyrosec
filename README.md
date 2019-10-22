# Gyrosec - 6.858 Spring 2019 Final Project - Jessy Lin, Jason Seibel

Use accelerometer and gyroscope sensor readings from a smartphone to determine the approximate locations of touches on the smartphone screen.

The Machine Learning Server accepts incoming data and processes it in a number of ways. The Expo Mobile App and React Native Android App are two ways of sending data to the server to be processed.

# Machine Learning Server

This python server will receive sensor data from either of our mobile apps and input this data whichever function you like. For example, running the hello function to record data to a csv file, running the predict function to predict touch locations, or running the plot_live function (called with the word "visualize") to plot the incoming data over time.

Modifications to the model used can be made by changing the code in the .ipynb files.

- `pip install -r requirements.txt`
- The server runs on port 8765 so consider making a tunnel for this port to connect it to the mobile app. For example `ngrok http 8765`
- `python server.py predict`, `python server.py visualize`, etc

# Expo Mobile App

Located in master branch in the folder "gyrosec". This app reads sensor data using Expo APIs and sends device dimensions, sensor readings, and touch press/release events to the server.

- `cd gyrosec`
-  `yarn install`
- Change the ngrok tunnel url to whatever url your server is running on. This is in App.js
-  `npm start`
- Now install Expo app on your smartphone
- Connect Expo app on smartphone to the running expo app seen after `npm start`. There are a number of ways to do this like scanning the QR code, connecting your Expo account, or sending a link from Expo to your smartphone. Refer to Expo documentation for most current information here.
- Once gyrosec is running on your smartphone it should immediately attempt to send data to your server url.

# React Native Android App

Located in branch "ejectedtest2" inside of the folder "gyrosec". This folder contains an Expo project that was ejected and uses Expokit. The android version of this project has new additional native java code that will register a foreground service that does all of the same work as our Expo Mobile App except it only sends device dimensions and sensor readings to the server url specified in "VIForegroundService.java".

- `cd gyrosec`
- `yarn install`
- `react-native link` You may need to install react-native as a global node module for this.
- Edit "VIForegroundService.java" to use a new server url instead of our ngrok url.
- `npm start`
- Now the Expo packager will be running. Leave this running, and additionally:
- Build the android project located in "gyrosec/android" - This could be done by opening the folder in android studio and building the project there.
- Install the android app on your smartphone.
- Upon running the app, it should connect to the Expo packager to run the app on your smartphone. Then the app should immediately attempt to send data to the server url.
