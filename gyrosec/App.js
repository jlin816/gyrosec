import React from 'react';
import { Dimensions, TouchableWithoutFeedback, Image, StyleSheet, Text, View } from 'react-native';
import { Gyroscope, Accelerometer } from 'expo';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      gyroscopeData: {},
      accData: {},
      wsReady: false,
    };
  }

  componentDidMount() {
    this.ws = new WebSocket("wss://7da67621.ngrok.io");
    console.log("Websocket initialized...");

    this.ws.onopen = () => {
      console.log("Websocket open!");
      this.setState({ wsReady: true });
      this.ws.send(JSON.stringify({
        "event": "info",
        "width": Dimensions.get('window').width,
        "height": Dimensions.get('window').height  
      }));
      console.log("Sent info");
    }
    console.log("Width: ", Dimensions.get('window').width);
    console.log("Height: ", Dimensions.get('window').height);

    Gyroscope.setUpdateInterval(16);
    Gyroscope.addListener(result => {
      this.setState({ gyroscopeData: result });
      if (this.state.wsReady) {
        //console.log("Sending to server!", result);
        this.ws.send(JSON.stringify({
          "event": "gyroscope",
          "data": result,
          "time": Date.now()
        }));
      }
    });

    Accelerometer.setUpdateInterval(16);
    Accelerometer.addListener(result => {
      this.setState({ accData: result });
      if (this.state.wsReady) {
        // console.log(result);
        this.ws.send(JSON.stringify({
          "event": "accelerometer",
          "data": result,
          "time": Date.now()
        }));
      }
    });
  }

  sendEvent(eventName, evt) {
    if (!this.state.wsReady) return;
    this.ws.send(JSON.stringify({
      "event": eventName,
      "locationX": evt.nativeEvent.locationX,
      "locationY": evt.nativeEvent.locationY,
      "time": Date.now()
    }));
  }

  render() {
    let { x, y, z } = this.state.gyroscopeData;

    return (
      <View style={styles.container}>
        <TouchableWithoutFeedback style={{ width: '100%', height: '100%' }}
          onPressIn={(evt) => this.sendEvent("press", evt)}
          onPressOut={(evt) => this.sendEvent("release", evt)}>
          <Image
            source={require('./passcode.png')}
            style={{width: '100%', height: '100%'}}
          />
        </TouchableWithoutFeedback>
      </View>
    );
  }
}

function round(n) {
  if (!n) {
    return 0;
  }

  return Math.floor(n * 100) / 100;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
