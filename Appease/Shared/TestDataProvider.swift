/*
See LICENSE folder for this sample’s licensing information.

Abstract:
TestDataProvider protocol defines the interface for providing payload for Watch Connectivity APIs.
 Its extension provides default payload for the coomands.
*/

import UIKit

// Constants to access the payload dictionary.
// isCurrentComplicationInfo is to tell if the userInfo is from transferCurrentComplicationUserInfo
// in session:didReceiveUserInfo: (see SessionDelegater).
//
struct PayloadKey {
    static let timeStamp = "timeStamp"
    static let isCurrentComplicationInfo = "isCurrentComplicationInfo"
}

// Constants to identify the app group container used for Settings-Watch.bundle and access
// the information in Settings-Watch.bundle.
//
struct WatchSettings {
    //static let sharedContainerID = "" // Specify your group container ID here and Root.plist to make watch settings work.
    static let sharedContainerID = "group.com.example.taehyo.SimpleWatchConnectivity"
    static let useLogFileForFileTransfer = "useLogFileForFileTransfer"
    static let clearLogsAfterTransferred = "clearLogsAfterTransferred"
}
