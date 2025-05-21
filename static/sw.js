self.addEventListener("push", event => {
    const data = event.data.text();
    self.registration.showNotification("🚨 Accident Alert", {
        body: data,
        icon: "/static/icon.png", // optional
    });
});
