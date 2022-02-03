import SwiftUI
import WatchConnectivity

struct ContentView: View {
	@State var isUserLoggedIn = false
    
    var body: some View {
        ZStack {
            if self.isUserLoggedIn {
                GameList()
            } else {
                TempView()
            }
        }
    }
}


struct TempView: View {
	//@EnvironmentObject var userStateManager: UserStateManager
	
	//@ObservedObject var model = TestWCWatch()
	@State var selection: String? = "False"
    @State var text = ""
    @State var messageText = ""
    
    @State var loggedIn = "False"
    
    var body: some View {
        
        VStack {
			Text(self.text)
            .onReceive(NotificationCenter.default.publisher(for: Notification.Name.fromIphone))
                    { obj in
                       // Change key as per your "userInfo"
                        if let userInfo = obj.userInfo, let info = userInfo["fromIPhone"] {
                            self.text = (info as AnyObject).description
                            print("inside onReceive")
                            print(self.text)
                       }
                    }
            .onReceive(NotificationCenter.default.publisher(for: Notification.Name.loginFromIphone))
                    { obj in
                       // Change key as per your "userInfo"
                        if let userInfo = obj.userInfo, let info = userInfo["loginFromIphone"] {
                            self.loggedIn = (info as AnyObject).description
                       }
                    }
            
            Text("Welcome! Please sign in using the app on your iPhone").padding()
            
			NavigationLink(
				destination: GameList(),
				label: {Text("Signed in")}
            ).disabled((self.loggedIn == "False"))
        }
    }
}


struct GameList: View {
    //    let tempURL = FileIOManager(directory: URL(fileURLWithPath: NSTemporaryDirectory(), isDirectory: true), fileName: ProcessInfo().globallyUniqueString)
    //    @State var messageData = ""
    //    @State var reachable = "No"
    
    @ObservedObject var healthStore = HealthStore()
    //var musicManager = MusicManager()
    @EnvironmentObject var userStateManager: UserStateManager
    
    var fileMetaData: [String: Any] {
        return ["file":"transferred" as Any]
    }
    
    var body: some View{
        List {
            NavigationLink(destination: FindAMatchView()){
                Text("Find A Match")
                    .navigationBarBackButtonHidden(false)
            }
            
            NavigationLink(
                destination: MemoryGameView(),
                label: {Text("Card Match")}
            )
            
            NavigationLink(
                destination: SensorDataView(healthStore: healthStore),
                label: {Text("Sensor Data")}
            )
            
            Button(action: {
                //musicManager.setupAudioPlayer(fileName: "example.mp3")
                //musicManager.activateAudioSession()
            }, label: {
                Text("Play Music")
            })
            
            Button(action: {
                //musicManager.stopPlayingAudio()
            }, label: {
                Text("Pause Music")
            })
            
            Button(action: {
                UserDefaults.standard.set(false, forKey: "ISUSERLOGGEDIN")
                //userStateManager.userLoggedOut()
            }, label: {
                Text("Log out")
            })
            
            //            Text("Reachable: \(reachable)")
            //
            //            Button(action: {
            //                if WatchConnectivityManager.sharedManager.isReachable() {
            //                    self.reachable = "Yes"
            //                } else {
            //                    self.reachable = "No"
            //                }
            //            }, label: {
            //                Text("Update reachability")
            //            })
            //
            //            Button(action: {
            //                _ = WatchConnectivityManager.sharedManager.transferFile(file: tempURL.fullURL, metadata: fileMetaData)
            //            }, label: {
            //                Text("File send to phone")
            //            })
            //
            //            TextField("Please enter message to send", text: $messageData)
            //
            //            Button(action: {
            //                WatchConnectivityManager.sharedManager.sendMessage(message: ["data": messageData], replyHandler: nil) { (error) in
            //                    print("Error \(error.localizedDescription)")
            //                }
            //            }, label: {
            //                Text("Send Data")
            //            })
        }
    }
}


struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
