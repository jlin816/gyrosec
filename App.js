import React from 'react';
import { TouchableWithoutFeedback, Image, StyleSheet, Text, View } from 'react-native';
import { Gyroscope, Accelerometer } from 'expo';
import BackgroundTimer from 'react-native-background-timer';
// let BackgroundTimer = require('react-native-background-timer').default

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      gyroscopeData: {},
      accData: {},
      wsReady: false,
    };
    this.ws = new WebSocket("ws://a06ece81.ngrok.io");

    this.ws.onopen = () => {
      console.log("Websocket open!");
      this.setState({ wsReady: true });
    }
  }

  componentDidMount() {
    // BackgroundTimer.runBackgroundTimer(() => { 
    // //code that will be called every 3 seconds 
    // console.log("hmm4")
    // }, 
    // 1000);
    // return
    // BackgroundTimer.start()
    // setTimeout(function(){ console.log("what a back round") }, 3000);
    // BackgroundTimer.stop()
    // Gyroscope.setUpdateInterval(16);
    // Gyroscope.addListener(result => {
    //   this.setState({ gyroscopeData: result });
    //   console.log(result)
    //   if (this.state.wsReady) {
    //     //console.log("Sending to server!", result);
    //     this.ws.send(JSON.stringify({
    //       "event": "gyroscope",
    //       "data": result,
    //       "time": Date.now()
    //     }));
    //   }
    // });
    function sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
    var blah = 0
    var parrcounter = 0
    var data=[]
    console.log("app code started")
    BackgroundTimer.runBackgroundTimer(() => { 
    //code that will be called every 3 seconds 
    //the below makes it so only one of these background threads is called
    if (blah!=0) {
      return
    }
    blah = 1

    //now real stuff
    console.log("hmmJ started")
    // Gyroscope.setUpdateInterval(16);
    // Gyroscope.addListener(result => {
    //   this.setState({ gyroscopeData: result });
    //   console.log(result)
    //   if (this.state.wsReady) {
    //     //console.log("Sending to server!", result);
    //     this.ws.send(JSON.stringify({
    //       "event": "gyroscope",
    //       "data": result,
    //       "time": Date.now()
    //     }));
    //   }
    // });

    Accelerometer.setUpdateInterval(16);
    Accelerometer.addListener(result => {
      this.setState({ accData: result });
      parrcounter+=1
      data+=result
      data+=Date.now()
      
      if (parrcounter % 500 == 0) {
        console.log(parrcounter)
        console.log(Date.now())
        // console.log(data)
        console.log("pretending to send data")
        fetch("http://2e58dcce.ngrok.io/a"+parrcounter)
        console.log("now resetting data so we can collect again")
        data = []
        parrcounter = 0
      }
      if (this.state.wsReady) {
        // console.log(result);
        this.ws.send(JSON.stringify({
          "event": "accelerometer",
          "data": result,
          "time": Date.now()
        }));
      }
    });
    console.log("got here infinite loop now")
    while (true) {

      // continue
      console.log("hii boi heartbeat")
      // await sleep(2000);
    }
    //below never occurs
    // setTimeout(function(){ console.log("what a back round") }, 1000);
    // await sleep(3000);

    //need to make code hang and never go farther
    // Gyroscope.setUpdateInterval(16);
    // Gyroscope.addListener(result => {
    //   this.setState({ gyroscopeData: result });
    //   console.log(result)
    //   if (this.state.wsReady) {
    //     //console.log("Sending to server!", result);
    //     this.ws.send(JSON.stringify({
    //       "event": "gyroscope",
    //       "data": result,
    //       "time": Date.now()
    //     }));
    //   }
    // });

    // Accelerometer.setUpdateInterval(16);
    // Accelerometer.addListener(result => {
    //   this.setState({ accData: result });
    //   console.log(result)
    //   if (this.state.wsReady) {
    //     // console.log(result);
    //     this.ws.send(JSON.stringify({
    //       "event": "accelerometer",
    //       "data": result,
    //       "time": Date.now()
    //     }));
    //   }
    // });
    console.log("ended")
    }, 
    3000);
    // Gyroscope.setUpdateInterval(16);
    // Gyroscope.addListener(result => {
    //   this.setState({ gyroscopeData: result });
    //   if (this.state.wsReady) {
    //     //console.log("Sending to server!", result);
    //     this.ws.send(JSON.stringify({
    //       "event": "gyroscope",
    //       "data": result,
    //       "time": Date.now()
    //     }));
    //   }
    // });

    // Accelerometer.setUpdateInterval(16);
    // Accelerometer.addListener(result => {
    //   this.setState({ accData: result });
    //   if (this.state.wsReady) {
    //     // console.log(result);
    //     this.ws.send(JSON.stringify({
    //       "event": "accelerometer",
    //       "data": result,
    //       "time": Date.now()
    //     }));
    //   }
    // });
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
