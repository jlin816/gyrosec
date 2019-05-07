import React from 'react';
import { TouchableWithoutFeedback, Image, StyleSheet, Text, View } from 'react-native';
import { Gyroscope, Accelerometer } from 'expo';
import BackgroundTimer from 'react-native-background-timer';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      gyroscopeData: {},
      accData: {},
      wsReady: false,
    };
    this.ws = new WebSocket("ws://52538153.ngrok.io");

    this.ws.onopen = () => {
      console.log("Websocket open!");
      this.setState({ wsReady: true });
    }
  }

  componentDidMount() {
    const a = BackgroundTimer.runBackgroundTimer(() => { 
      //code that will be called every 3 seconds
      console.log("lol")
      this.wsBack = new WebSocket("ws://52538153.ngrok.io");

      this.wsBack.onopen = () => {
        console.log("Websocket Background open!");
        this.setState({ wsReady: true });
      }
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

    }, 
    3000);
//rest of code will be performing for iOS on background too

// BackgroundTimer.stopBackgroundTimer(); //after this call all code on background stop run.
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
