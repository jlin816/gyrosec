
function sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = async (taskData) => {
  // do stuff
  while (true) {
    console.log("testing J A J A J")
    sleep(2000)
  }
};