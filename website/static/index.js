function deleteAircraft(aircraftId) {
    console.log("Delete Called");
    fetch("/delete-aircraft", {
      method: "POST",
      body: JSON.stringify({ aircraftId: aircraftId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }