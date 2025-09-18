"use strict";

const postcode = document.getElementById('id_postal_code');
const prefecture = document.getElementById('id_prefecture');
const city = document.getElementById('id_city');
const streetAddress = document.getElementById('id_street_address');
const errorDiv = document.getElementById('postcode-error');

if (postcode) {
  postcode.addEventListener('input', function (e) {
    const postalcode = e.target.value.replace(/[^0-9]/g, '');
    e.target.value = postalcode;

    if (postalcode.length < 7) {
      if (errorDiv) {
        errorDiv.textContent = '郵便番号は7桁で入力してください。';
        errorDiv.style.display = 'block';
      }
      return;
    }

    // 7桁ちょうどになったらメッセージ非表示
    if (postalcode.length === 7 && errorDiv) {
      errorDiv.textContent = '';
      errorDiv.style.display = 'none';
    }

    const url = `https://postcode.teraren.com/postcodes/${postalcode}.json`;

    fetch(url)
      .then(response => response.json())
      .then(json => {
        if (prefecture) prefecture.value = json.prefecture || '';
        if (city) city.value = json.city || '';
        if (streetAddress) streetAddress.value = json.suburb || '';
      })
      .catch(error => {
        console.error(error);
        [prefecture, city, streetAddress].forEach(el => {
          if (el) el.value = '';
        });
        if (errorDiv) {
          errorDiv.textContent = '住所の取得に失敗しました。手動で入力してください。';
          errorDiv.style.display = 'block';
        }
      });
  });
}
