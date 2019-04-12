import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Gyroscope } from 'expo';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      gyroscopeData: {},
    };
    this.ws = new WebSocket("wss://localhost:8765");
  }

  componentDidMount() {
    Gyroscope.setUpdateInterval(16);
    this._subscription = Gyroscope.addListener(result => {
      this.setState({ gyroscopeData: result });
      console.log(result);
      this.ws.send(result);
    });
  }

  render() {
    let { x, y, z } = this.state.gyroscopeData;

    return (
      <View style={styles.container}>
        <Text>Open up App.js to start working on your app!</Text>
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
