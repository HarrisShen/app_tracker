function getCurrTime() {
    function twoDigits(num) {return (num < 10 ? '0' : '') + num.toString();}
    const now = new Date();
    return (now.getFullYear() + '-' + twoDigits(now.getMonth() + 1) + '-' + twoDigits(now.getDate()) +
        'T' + twoDigits(now.getHours()) + ':' + twoDigits(now.getMinutes()));
}

function getTimeDiff(t1, t2 = null) {
  if (t2 === null) t2 = Date.now();
  dt = t2 - t1;
  return dt;
}

// turning the time in ms difference to a descriptive string
function timeDiffToString(td) {
  td = Math.floor(td / 1000);
  if (td < 60) return "Just now";
  td = Math.floor(td / 60);
  if (td < 60) return td + "minutes ago";
  td = Math.floor(td / 60);
  if (td < 24) return td + "hours ago";
  td = Math.floor(td / 24);
  if (td < 7) return td + "days ago";
  wks = Math.floor(td / 7);
  if (td < 30) return wks + "weeks ago";
  return "> 1 month ago";
}

async function postData(url = '', data = {}) {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }