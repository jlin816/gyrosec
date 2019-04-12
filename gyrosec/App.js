import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Gyroscope } from 'expo';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      gyroscopeData: {},
      wsReady: false,
    };
    this.ws = new WebSocket("ws://930b299f.ngrok.io");

    this.ws.onopen = () => {
      console.log("Websocket open!");
      this.setState({ wsReady: true });
    }
  }

  componentDidMount() {
    Gyroscope.setUpdateInterval(1000);
    this._subscription = Gyroscope.addListener(result => {
      this.setState({ gyroscopeData: result });
      if (this.state.wsReady) {
        console.log("Sending to server!", result);
        this.ws.send(JSON.stringify(result));
      }
    });
  }

  render() {
    let { x, y, z } = this.state.gyroscopeData;

    return (
      <View style={styles.container}>
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
