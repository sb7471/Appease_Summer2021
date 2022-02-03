/*
See LICENSE folder for this sample’s licensing information.

Abstract:
The app delegate class of the iOS app.
*/

import UIKit
import WatchConnectivity
import HealthKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
	private let healthStore = HKHealthStore()

    var window: UIWindow?
    
    private lazy var sessionDelegater: SessionDelegater = {
        return SessionDelegater()
    }()

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplicationLaunchOptionsKey: Any]?) -> Bool {
        
        // Trigger WCSession activation at the early phase of app launching.
        //
        assert(WCSession.isSupported(), "This sample requires Watch Connectivity support!")
        WCSession.default.delegate = sessionDelegater
        WCSession.default.activate()
        
        // Remind the setup of WatchSettings.sharedContainerID.
        //
        if WatchSettings.sharedContainerID.isEmpty {
            print("Specify a shared container ID for WatchSettings.sharedContainerID to use watch settings!")
        }

        return true
    }
	
	// MARK: UISceneSession Lifecycle

	func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
		// Called when a new scene session is being created.
		// Use this method to select a configuration to create the new scene with.
		return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
	}

	func application(_ application: UIApplication, didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {
		// Called when the user discards a scene session.
		// If any sessions were discarded while the application was not running, this will be called shortly after application:didFinishLaunchingWithOptions.
		// Use this method to release any resources that were specific to the discarded scenes, as they will not return.
	}
	
	// authorization from watch
	func applicationShouldRequestHealthAuthorization(_ application: UIApplication) {
		// Authorize access to health data for watch.
		healthStore.handleAuthorizationForExtension { success, error in
			print(success)
		}
	}
}
