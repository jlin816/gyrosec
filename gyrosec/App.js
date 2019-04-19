import React from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';
import { Gyroscope, Accelerometer } from 'expo';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      gyroscopeData: {},
      accData: {},
      wsReady: false,
    };
    this.ws = new WebSocket("ws://930b299f.ngrok.io");

    this.ws.onopen = () => {
      console.log("Websocket open!");
      this.setState({ wsReady: true });
    }
  }

  componentDidMount() {
    const startTime = Date.now();
    Gyroscope.setUpdateInterval(16);
    Gyroscope.addListener(result => {
      this.setState({ gyroscopeData: result });
      if (this.state.wsReady) {
        //console.log("Sending to server!", result);
        //this.ws.send(JSON.stringify(result));
      }
    });

    Accelerometer.setUpdateInterval(500);
    Accelerometer.addListener(result => {
      this.setState({ accData: result });
      if (this.state.wsReady) {
        result["time"] = Date.now() - startTime;
        console.log(result);
        this.ws.send(JSON.stringify(result));
      }
    });

  }

  render() {
    let { x, y, z } = this.state.gyroscopeData;

    return (
      <View style={styles.container}>
        <Image
          source={require('./passcode.png')}
          style={{width: '100%', height: '100%'}}
        />
        <Text>
          x: {round(x)} y: {round(y)} z: {round(z)}
        </Text>
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
