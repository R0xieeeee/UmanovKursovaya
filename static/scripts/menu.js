function filterProducts(category) {
    const productList = document.getElementById('product-list');
    const products = productList.querySelectorAll('.product');

    products.forEach(product => {
        if (category === 'all' || product.dataset.category === category) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });

    const categoryButtons = document.querySelectorAll('.category-buttons button');
    categoryButtons.forEach(btn => {
        if (btn.textContent === category || (category === 'all' && btn.textContent === 'Все')) {
            btn.classList.add('active-category');
        } else {
            btn.classList.remove('active-category');
        }
    });
}
