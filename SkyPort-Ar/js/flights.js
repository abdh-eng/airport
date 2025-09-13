$(document).ready(function () {
  const $tbody = $('#flights-table tbody');
  const $pagination = $('#pagination');
  let flights = [];
  let currentPage = 1;
  const pageSize = 8;

  // تحميل البيانات من JSON
  function loadFlights() {
    return $.getJSON('/data/flights.json') // تأكد أن المسار صحيح
      .done(function (data) {
        flights = data;
        renderTable();
      })
      .fail(function () {
        toastr.error('فشل تحميل بيانات الرحلات');
      });
  }

  // دالة لتحديد لون حالة الرحلة
  function statusClass(s) {
    if (!s) s = '';
    s = s.toLowerCase();
    if (s.includes('delayed')) return 'bg-danger';
    if (s.includes('boarding')) return 'bg-success';
    if (s.includes('cancelled')) return 'bg-dark';
    return 'bg-secondary'; // On Time أو أي حالة أخرى
  }

  // عرض الجدول
  function renderTable() {
    $tbody.empty();
    const start = (currentPage - 1) * pageSize;
    const pageItems = flights.slice(start, start + pageSize);

    if (pageItems.length === 0) {
      $tbody.append('<tr><td colspan="8" class="text-center small text-muted">لا توجد نتائج</td></tr>');
      renderPagination();
      return;
    }

    pageItems.forEach(f => {
      const tr = $('<tr>');
      tr.append($('<td>').text(f.code || '-'));
      tr.append($('<td>').text(f.airline || '-'));
      tr.append($('<td>').text(f.destination || '-'));
      tr.append($('<td>').text(f.departure_time || '-'));
      tr.append($('<td>').text(f.arrival_time || '-'));
      tr.append($('<td>').text(f.gate || '-'));
      tr.append($('<td>').html('<span class="badge ' + statusClass(f.status) + '">' + (f.status || '-') + '</span>'));
      tr.append($('<td>').html('<button class="btn btn-sm btn-outline-primary details-btn" data-code="' + f.code + '">تفاصيل</button>'));
      $tbody.append(tr);
    });

    renderPagination();
  }

  // عرض Pagination
  function renderPagination() {
    $pagination.empty();
    const totalPages = Math.max(1, Math.ceil(flights.length / pageSize));

    for (let i = 1; i <= totalPages; i++) {
      const li = $('<li>').addClass('page-item ' + (i === currentPage ? 'active' : ''));
      const a = $('<a>').addClass('page-link').attr('href', '#').text(i).on('click', function (e) {
        e.preventDefault();
        currentPage = i;
        renderTable();
      });
      li.append(a);
      $pagination.append(li);
    }
  }

  // تطبيق الفلاتر والبحث والفرز
  function applyFilters() {
    const q = ($('#flight-search').val() || '').toLowerCase().trim();
    const status = $('#filter-status').val();
    const sortBy = $('#sort-by').val();
    let list = flights.slice(); // نسخة من البيانات

    // فلتر حسب الحالة
    if (status) list = list.filter(x => (x.status || '').toLowerCase() === status.toLowerCase());

    // فلتر حسب البحث
    if (q) {
      list = list.filter(x => {
        const str = (x.code + ' ' + x.destination + ' ' + x.airline).toLowerCase();
        return str.indexOf(q) !== -1;
      });
    }

    // فرز
    list.sort(function (a, b) {
      if (sortBy === 'departure_time') return (a.departure_time || '').localeCompare(b.departure_time || '');
      if (sortBy === 'destination') return (a.destination || '').localeCompare(b.destination || '');
      if (sortBy === 'code') return (a.code || '').localeCompare(b.code || '');
      return 0;
    });

    flights = list;
    currentPage = 1;
    renderTable();
  }

  // فتح تفاصيل الرحلة في Modal
  $(document).on('click', '.details-btn', function () {
    const code = $(this).data('code');
    const f = flights.find(x => x.code === code);
    if (!f) {
      toastr.error('الرحلة غير موجودة');
      return;
    }

    const html = `
      <h4>${f.code || '-'} — ${f.destination || '-'}</h4>
      <p><strong>شركة الطيران:</strong> ${f.airline || '-'}</p>
      <p><strong>الإقلاع:</strong> ${f.departure_time || '-'}</p>
      <p><strong>الوصول:</strong> ${f.arrival_time || '-'}</p>
      <p><strong>البوابة:</strong> ${f.gate || '-'}</p>
      <p><strong>الحالة:</strong> ${f.status || '-'}</p>
      <p><strong>ملاحظات:</strong> ${f.notes || '-'}</p>
    `;

    $('#flight-details').html(html);
    const modal = new bootstrap.Modal(document.getElementById('flightModal'));
    modal.show();

    $('#book-btn').off('click').on('click', function () {
      toastr.success('تم حجز مقعد (تجريبي) في الرحلة ' + f.code);
      modal.hide();
    });
  });

  // أحداث البحث والفلتر والفرز
  $('#search-btn').on('click', applyFilters);
  $('#filter-status, #sort-by').on('change', applyFilters);

  // تحميل البيانات أولاً
  loadFlights();
});
