function approveDoc(filename, endpoint) {
    fetch(`/${endpoint}/approve/${filename}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) location.reload();
        });
}
function declineDoc(filename, endpoint) {
    let reason = prompt("Reason for declining:");
    if (reason) {
        fetch(`/${endpoint}/decline/${filename}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: reason })
        }).then(res => res.json())
          .then(data => { if (data.success) location.reload(); });
    }
}