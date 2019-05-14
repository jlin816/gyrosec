import React from 'react';
import { AppRegistry, Platform, Button, TouchableWithoutFeedback, Image, StyleSheet, Text, View } from 'react-native';
import { Gyroscope, Accelerometer } from 'expo';
import BackgroundTimer from 'react-native-background-timer';
// let BackgroundTimer = require('react-native-background-timer').default


// AppRegistry.registerHeadlessTask('SomeTaskName', () => require('SomeTaskName'));

import VIForegroundService from '@voximplant/react-native-foreground-service';

// const channelConfig = {
//     id: 'channelId',
//     name: 'Channel name',
//     description: 'Channel description',
//     enableVibration: false
// };
// VIForegroundService.createNotificationChannel(channelConfig);


// async startForegroundService()  {
//   console.log("tryingggggg")
//     const notificationConfig = {
//         channelId: 'channelId',
//         id: 3456,
//         title: 'Title',
//         text: 'Some text',
//         icon: 'ic_icon'
//     };
//     try {
//       console.log("tryingggggg")
//         await VIForegroundService.startService(notificationConfig);
//     } catch (e) {
//         console.error(e);
//     }
// }
// startForegroundService()



function sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
}
    var blah = 0
    var parrcounter = 0
    var data=[]
    console.log("app code started")
    const intervalId = BackgroundTimer.runBackgroundTimer(async () => { 
    //code that will be called every 3 seconds 
    //the below makes it so only one of these background threads is called
    // console.log("initial play")
    if (blah!=0) {
      return
    }
    blah = 1

    function getMethods(obj) {
      var result = [];
      for (var id in obj) {
        try {
          if (typeof(obj[id]) == "function") {
            result.push(id + ": " + obj[id].toString());
          }
        } catch (err) {
          result.push(id + ": inaccessible");
        }
      }
      return result;
    }
    console.log("jasontest")
    console.log(getMethods(VIForegroundService))

    //now real stuff
    console.log("hmmJ started")
    // startForegroundService()
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
    Accelerometer.addListener((result) => {
      // this.setState({ accData: result });
      parrcounter+=1
      data+=result
      data+=Date.now()
      if (parrcounter % 50 == 0) {
        console.log("data heartbeat 50")
      }
      
      if (parrcounter % 500 == 0) {
        console.log(parrcounter)
        console.log(Date.now())
        // console.log(data)
        console.log("pretending to send data")
        fetch("http://89ad9f3e.ngrok.io/a"+parrcounter)
        console.log("now resetting data so we can collect again")
        data = []
        parrcounter = 0
      }
      // if (this.state.wsReady) {
      //   // console.log(result);
      //   this.ws.send(JSON.stringify({
      //     "event": "accelerometer",
      //     "data": result,
      //     "time": Date.now()
      //   }));
      // }
    });
    console.log("got here infinite loop now")
    while (true) {

      // continue
      console.log("hii boi heartbeat")
      await sleep(2000);
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
    1000);

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

  async startService() {
  console.log("sup boiiiiiiiiiiiiiiiiiiiiiiii")
        if (Platform.OS !== 'android') {
            console.log('Only Android platform is supported');
            return;
        }
        if (Platform.Version >= 26) {
            const channelConfig = {
                id: 'ForegroundServiceChannel',
                name: 'Notification Channel',
                description: 'Notification Channel for Foreground Service',
                enableVibration: false,
                importance: 2
            };
            await VIForegroundService.createNotificationChannel(channelConfig);
        }
        const notificationConfig = {
            id: 3456,
            title: 'Foreground Service',
            text: 'Foreground service is running',
            icon: 'ic_notification',
            priority: 0
        };
        if (Platform.Version >= 26) {
            notificationConfig.channelId = 'ForegroundServiceChannel';
        }
        await VIForegroundService.startService(notificationConfig);
    return
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
    // function sleep(ms) {
    //   return new Promise(resolve => setTimeout(resolve, ms));
    // }
    // var blah = 0
    // var parrcounter = 0
    // var data=[]
    // console.log("app code started")
    // const intervalId = BackgroundTimer.runBackgroundTimer(async () => { 
    // //code that will be called every 3 seconds 
    // //the below makes it so only one of these background threads is called
    // // console.log("initial play")
    // if (blah!=0) {
    //   return
    // }
    // blah = 1

    // //now real stuff
    // console.log("hmmJ started")
    // // Gyroscope.setUpdateInterval(16);
    // // Gyroscope.addListener(result => {
    // //   this.setState({ gyroscopeData: result });
    // //   console.log(result)
    // //   if (this.state.wsReady) {
    // //     //console.log("Sending to server!", result);
    // //     this.ws.send(JSON.stringify({
    // //       "event": "gyroscope",
    // //       "data": result,
    // //       "time": Date.now()
    // //     }));
    // //   }
    // // });

    // Accelerometer.setUpdateInterval(16);
    // Accelerometer.addListener(result => {
    //   this.setState({ accData: result });
    //   parrcounter+=1
    //   data+=result
    //   data+=Date.now()
    //   if (parrcounter % 50 == 0) {
    //     console.log("data heartbeat 50")
    //   }
      
    //   if (parrcounter % 500 == 0) {
    //     console.log(parrcounter)
    //     console.log(Date.now())
    //     // console.log(data)
    //     console.log("pretending to send data")
    //     fetch("http://ebd10a09.ngrok.io/a"+parrcounter)
    //     console.log("now resetting data so we can collect again")
    //     data = []
    //     parrcounter = 0
    //   }
    //   if (this.state.wsReady) {
    //     // console.log(result);
    //     this.ws.send(JSON.stringify({
    //       "event": "accelerometer",
    //       "data": result,
    //       "time": Date.now()
    //     }));
    //   }
    // });
    // console.log("got here infinite loop now")
    // while (true) {

    //   // continue
    //   console.log("hii boi heartbeat")
    //   await sleep(2000);
    // }
    // //below never occurs
    // // setTimeout(function(){ console.log("what a back round") }, 1000);
    // // await sleep(3000);

    // //need to make code hang and never go farther
    // // Gyroscope.setUpdateInterval(16);
    // // Gyroscope.addListener(result => {
    // //   this.setState({ gyroscopeData: result });
    // //   console.log(result)
    // //   if (this.state.wsReady) {
    // //     //console.log("Sending to server!", result);
    // //     this.ws.send(JSON.stringify({
    // //       "event": "gyroscope",
    // //       "data": result,
    // //       "time": Date.now()
    // //     }));
    // //   }
    // // });

    // // Accelerometer.setUpdateInterval(16);
    // // Accelerometer.addListener(result => {
    // //   this.setState({ accData: result });
    // //   console.log(result)
    // //   if (this.state.wsReady) {
    // //     // console.log(result);
    // //     this.ws.send(JSON.stringify({
    // //       "event": "accelerometer",
    // //       "data": result,
    // //       "time": Date.now()
    // //     }));
    // //   }
    // // });
    // console.log("ended")
    // }, 
    // 1000);
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
      <Button title="Start foreground service" onPress={() => this.startService()}/>
        {/*<TouchableWithoutFeedback style={{ width: '20%', height: '20%' }}
          onPressIn={(evt) => this.sendEvent("press", evt)}
          onPressOut={(evt) => this.sendEvent("release", evt)}>
          <Image
            source={require('./passcode.png')}
            style={{width: '100%', height: '100%'}}
          />
        </TouchableWithoutFeedback>*/}
        <Text>Jason Test</Text>
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
