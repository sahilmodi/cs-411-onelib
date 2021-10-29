window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple);
    }

    const datatableAvailBooks = document.getElementById('AvailableBooks');
    if (datatableAvailBooks) {
        new simpleDatatables.DataTable(datatableAvailBooks);
    }

    const databaseBorrowedBooks = document.getElementById('BorrowedBooks');
    if (databaseBorrowedBooks) {
        new simpleDatatables.DataTable(databaseBorrowedBooks);
    }
});

function onRowClick() {
    alert('hello')
}