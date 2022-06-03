import React, { useEffect, useRef, useState, Dispatch } from "react";
import { useAppSelector, useAppDispatch } from '../hooks'
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";


let Map = () => {

    const [map, setMap] = useState<mapboxgl.Map | null>(null);
    const mapRef = useRef<HTMLDivElement>(null);
    const bbox = useAppSelector(state => state.route.selectedRouteBBox)
    const route = useAppSelector(state => state.route.selectedRoute?.id)

    const MAP_CONTAINER_ID = "map-container";

    const loadTiles = (map: mapboxgl.Map) => {

        map.addLayer({
            "id": "django-tiles",
            "type": "line",
            "source": {

                type: 'vector',
                tiles: ['http://localhost:9202/route/tiles?tile={z}/{x}/{y}'],
                minzoom: 1,
                maxzoom: 8,
            },
            "source-layer": "default",
            "layout": {
                "line-join": "round",
                "line-cap": "round"
            },
            "paint": {
                "line-color": "#ff69b4",
                "line-width": 1
            }
        });

    }

    useEffect(() => {

        mapboxgl.accessToken =
            "pk.eyJ1IjoiYXphdmVhIiwiYSI6IkFmMFBYUUUifQ.eYn6znWt8NzYOa3OrWop8A";
        const initializeMap = (setMap: Dispatch<mapboxgl.Map>) => {
            var [xmin, ymin, xmax, ymax] = [
                -20.026114086648512,
                -13.080309755245814,
                19.700190980283185,
                12.703790184833048,
            ];

            var url = new URL(window.location.href);
            var embedParam = url.searchParams.get("embed");
            const embed = embedParam === "true" ? true : false;

            const map = new mapboxgl.Map({
                container: MAP_CONTAINER_ID,
                style: 'mapbox://styles/mapbox/dark-v10',
                center: [0, 10],
                bearing: 0,
                pitch: 0,
                minZoom: 2.1,
                maxZoom: 11,
                //hash: false,
                // maxBounds: [
                //     [xmin - 40, ymin - 40],
                //     [xmax + 40, ymax + 40],
                // ],
            });

            var nav = new mapboxgl.NavigationControl({
                showCompass: false,
                showZoom: true,
            });

            map.addControl(nav, "top-left");


            // map.fitBounds(
            //     [
            //         [xmax, ymax],
            //         [xmin, ymin],
            //     ],
            //     {
            //         padding: embed
            //             ? 5
            //             : {
            //                 left: 10,
            //                 right: 340,
            //                 top: 0,
            //                 bottom: 0,
            //             },
            //     }
            // );
            //initZoomToState(map);
            map.dragRotate.disable();
            map.doubleClickZoom.disable();
            map.touchZoomRotate.disableRotation();
            map.on("load", () => {
                console.log('onLoad')
                setMap(map);
                loadTiles(map);
                //loadMap(map);
            });
            //window.history.replaceState({}, "", "/");
        };

        if (!map) {
            initializeMap(setMap);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [map]);

    useEffect(() => {
        if (bbox.length) {
            map && map.fitBounds(
                [
                    [bbox[2], bbox[3]],
                    [bbox[0], bbox[1]],
                ])
        }
        else {
            map && map.flyTo({
                center: [0, 10],
                zoom: 2.1
            })
        }
    }, [bbox, map])

    useEffect(() => {
        if (route) {
            const lineColorOverlay = ["match", ["get", "id"], route, "#fff", "#ff69b4"]
            const lineWidthOverlay = ["match", ["get", "id"], route, 5, 1]
            map && map.setPaintProperty('django-tiles', 'line-color', lineColorOverlay)
            map && map.setPaintProperty('django-tiles', 'line-width', lineWidthOverlay)
        }
        else {
            map && map.setPaintProperty('django-tiles', 'line-color', "#ff69b4")
            map && map.setPaintProperty('django-tiles', 'line-width', 1)
        }
    }, [route, map])


    return (
        <React.Fragment>
            <div id="map-container" ref={mapRef} />
        </React.Fragment>
    );
}

export default Map;