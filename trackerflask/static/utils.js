function getCurrTime() {
    function twoDigits(num) {return (num < 10 ? '0' : '') + num.toString();}
    const now = new Date();
    return (now.getFullYear() + '-' + twoDigits(now.getMonth() + 1) + '-' + twoDigits(now.getDate()) +
        'T' + twoDigits(now.getHours()) + ':' + twoDigits(now.getMinutes()));
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