function deleteAircraft(aircraftId) {
    console.log("Delete Aircraft Called");
    fetch("/delete-aircraft", {
      method: "POST",
      body: JSON.stringify({ aircraftId: aircraftId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }

function deleteUser(userId) {
  console.log("Delete User Called");
  fetch("/delete-user", {
    method: "POST",
    body: JSON.stringify({ userId: userId }),
  }).then((_res) => {
    window.location.href = "/users";
  });
}



// Function to hide the Spinner 
function hideSpinner() { 
  document.getElementById('spinner') 
          .style.display = 'none'; 
}  

// FROM :
// https://github.com/codebasics/python_projects_grocery_webapp
// https://www.youtube.com/watch?v=RsK70V-R2N0

var loadpointModal = $("#loadpointModal");
  $(function () {

  });

  // Save Load Point
  $("#saveLoadpoint").on("click", function () {
    
    // var data = $("#loadpointForm").serializeArray();
    var data = $("#loadpointForm").serializeArray();

    for (var i=0;i<data.length;++i) {
        var element = data[i];
        switch(element.name) {
            case 'name':
                var lp = element.value;
                break;
            case 'cg_distance':
                var cg = element.value;
                break;
        }
    }
    var load_points_field = document.getElementById("loading_points");
    try {
      var load_point_dict = JSON.parse(load_points_field.value);
    } catch(e) {
      // alert(e)
      var load_point_dict = {"empty_weight": 0, "pilot": 0, "fuel": 0}
    }
    if (load_point_dict.length == 0) {
      var load_point_dict = []
    };
    console.log(load_point_dict)
    load_point_dict[lp] = parseFloat(cg);

    load_points_field.value = JSON.stringify(load_point_dict);
    console.table(load_point_dict)

    // callApi("POST", productSaveApiUrl, {
    //     'data': JSON.stringify(requestPayload)
    // });
});

  loadpointModal.on('show.bs.modal', function(){
    //JSON data by API call
    // $.get(uomListApiUrl, function (response) {
    //     if(response) {
    //         var options = '<option value="">--Select--</option>';
    //         $.each(response, function(index, uom) {
    //             options += '<option value="'+ uom.uom_id +'">'+ uom.uom_name +'</option>';
    //         });
    //         $("#uoms").empty().html(options);
    //     }
    var options = '<option value="">--Select--</option>';
    
    options += '<option value="enhet">Namn</option>';
    $("#uoms").empty().html(options);
    // });
  });

function clearEnvelope() {
  var envelope_field = document.getElementById("envelope");
  envelope_field.value = "";
};

function clearLoadpoints() {
  var envelope_field = document.getElementById("loading_points");
  envelope_field.value = "";
};

var envelopeModal = $("#envelopeModal");
$(function () {


  });

  // Save Load Point
  $("#saveEnvelope").on("click", function () {
    var data = $("#envelopeForm").serializeArray();

    for (var i=0;i<data.length;++i) {
        var element = data[i];
        switch(element.name) {
            case 'weight':
                var weight = element.value;
                break;
            case 'cg_envelope':
                var cg = element.value;
                break;
        }
    }
    var envelope_field = document.getElementById("envelope");
    try {
      var envelope = envelope_field.value;
    } catch(e) {
      // alert(e)
      var envelope = ""
    }
    if (envelope.length == 0) {
      var envelope = ""
    };
    console.log(envelope)
    envelope += "(" + parseFloat(cg) + "," + weight + "),";

    envelope_field.value = envelope;
    console.table(envelope)

    // callApi("POST", productSaveApiUrl, {
    //     'data': JSON.stringify(requestPayload)
    // });
});

  envelopeModal.on('show.bs.modal', function(){
    //JSON data by API call
    // $.get(uomListApiUrl, function (response) {
    //     if(response) {
    //         var options = '<option value="">--Select--</option>';
    //         $.each(response, function(index, uom) {
    //             options += '<option value="'+ uom.uom_id +'">'+ uom.uom_name +'</option>';
    //         });
    //         $("#uoms").empty().html(options);
    //     }
    var options = '<option value="">--Select--</option>';
    
    options += '<option value="enhet">Namn</option>';
    $("#uoms").empty().html(options);
    // });
  });