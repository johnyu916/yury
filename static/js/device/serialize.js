/* save to and load from json
 *
 */
function get_device(data){
    var data_devices = data['devices'];
    var devices = [];
    for (var i = 0; i < data_devices.length; i++){
        var data_device = data_devices[i];
        var device = get_device(data_device);
        devices.push(device);
    }
    var data_sources = data['sources'];
    for (var i = 0; i < data_sources.length; i++){
        var data_source = data_sources[i];
        var source = new Source(data_source[name],);
        var device = 
        devices.push(device);
    }
    var device = new Device(data['name']);
    device.devices = devices;
}

function get_dictionary(device){
    var data = {
        'name': device.name,
        'devices': [],
        'sources': [],
        'grounds': [],
        'resistors': [],
        'switches': [],
        'wires': [],
        'bridges': []
    }

    for (device in device.devices){
        var deviceData = saveDevice(device);
        data['devices'].push(deviceData);
    }
    for (source in device.sources){
        var sourceData = {
            'name': source.name;
            'to': source.to.name;
        }
        data['sources'].push(sourceData);
    }
    for (ground in device.grounds){
        var groundData = {
            'name': ground.name;
            'from': ground.from.name;
        }
        data['sources'].push(groundData);
    }
    for (resistor in device.resistors){
        var resistorData = {
            'name': resistor.name;
            'from': resistor.from.name;
            'to': resistor.to.name;
        }
        data['resistors'].push(resistorData);
    }
    for (element in device.switches){
        var switchData = {
            'name': element.name;
            'from': element.from.name;
            'to': element.to.name;
            'button': element.button.name;
        }
        data['resistors'].push(resistorData);
    }
    for (var i =0; i <device.wires.length; i++){
        var wire = device.wires[i];
        var wireData = {
            'name': wire.name;
            'from': wire.from.name;
            'to': wire.to.name;
        }
        data['wires'].push(wireData);

    }
    return data
}
