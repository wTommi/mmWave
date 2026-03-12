//
//  MapView.swift
//  mmWave
//
//  Created by Tommi on 2026/2/23.
//

import CoreLocation
import Combine

class LocationManager: NSObject, ObservableObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()

    @Published var pathCoordinates: [CLLocationCoordinate2D] = []
    
    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBestForNavigation
        manager.distanceFilter = 2.0
        
        manager.requestWhenInUseAuthorization()
        manager.startUpdatingLocation()
    }
    
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let latestLocation = locations.last else { return }

        if latestLocation.horizontalAccuracy < 0 || latestLocation.horizontalAccuracy > 20 {
            return
        }

        DispatchQueue.main.async {
            self.pathCoordinates.append(latestLocation.coordinate)
        }
    }
}
