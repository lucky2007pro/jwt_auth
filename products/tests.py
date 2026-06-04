from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from accounts.models import CustomUser, SELLER, ORDINARY_USER
from .models import Category, Brand, Product, ProductImage


# ============================================
# MODEL TESTLARI
# ============================================

class CategoryModelTest(TestCase):
    """Category modeli uchun testlar"""

    def setUp(self):
        """Test uchun dastlabki ma'lumotlar"""
        self.parent_category = Category.objects.create(
            name="Elektronika",
            is_active=True
        )
        self.child_category = Category.objects.create(
            name="Telefonlar",
            parent=self.parent_category,
            is_active=True
        )

    def test_category_creation(self):
        """Kategoriya yaratilishini tekshirish"""
        self.assertEqual(self.parent_category.name, "Elektronika")
        self.assertTrue(self.parent_category.is_active)
        self.assertIsNone(self.parent_category.parent)

    def test_category_slug_auto_generation(self):
        """Slug avtomatik yaratilishini tekshirish"""
        self.assertEqual(self.parent_category.slug, "elektronika")

    def test_category_str_method(self):
        """__str__ metodini tekshirish"""
        self.assertEqual(str(self.parent_category), "Elektronika")
        self.assertEqual(str(self.child_category), "Elektronika → Telefonlar")

    def test_category_full_path_property(self):
        """full_path property tekshiruvi"""
        self.assertEqual(self.parent_category.full_path, "Elektronika")
        self.assertEqual(self.child_category.full_path, "Elektronika → Telefonlar")

    def test_duplicate_slug_handling(self):
        """Bir xil nom bilan kategoriya yaratganda slug o'zgarishini tekshirish"""
        duplicate = Category.objects.create(name="Elektronika")
        self.assertEqual(duplicate.slug, "elektronika-1")


class BrandModelTest(TestCase):
    """Brand modeli uchun testlar"""

    def setUp(self):
        self.brand = Brand.objects.create(
            name="Samsung",
            description="Samsung Electronics",
            is_active=True
        )

    def test_brand_creation(self):
        """Brend yaratilishini tekshirish"""
        self.assertEqual(self.brand.name, "Samsung")
        self.assertTrue(self.brand.is_active)

    def test_brand_slug_generation(self):
        """Slug yaratilishini tekshirish"""
        self.assertEqual(self.brand.slug, "samsung")


class ProductModelTest(TestCase):
    """Product modeli uchun testlar"""

    def setUp(self):
        self.seller = CustomUser.objects.create_user(
            username="seller1",
            email="seller@test.com",
            password="test123",
            user_role=SELLER
        )
        self.category = Category.objects.create(name="Telefonlar")
        self.brand = Brand.objects.create(name="Samsung")

        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            brand=self.brand,
            name="Samsung Galaxy S24",
            description="Zo'r telefon",
            price=Decimal("1000.00"),
            discount_price=Decimal("800.00"),
            stock=10
        )

    def test_product_creation(self):
        """Mahsulot yaratilishini tekshirish"""
        self.assertEqual(self.product.name, "Samsung Galaxy S24")
        self.assertEqual(self.product.price, Decimal("1000.00"))
        self.assertEqual(self.product.stock, 10)

    def test_product_slug_generation(self):
        """Slug yaratilishini tekshirish"""
        self.assertEqual(self.product.slug, "samsung-galaxy-s24")

    def test_is_in_stock_property(self):
        """is_in_stock property tekshiruvi"""
        self.assertTrue(self.product.is_in_stock)

        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock)

    def test_discount_percentage_property(self):
        """discount_percentage hisoblashni tekshirish"""
        # (1 - 800/1000) * 100 = 20%
        self.assertEqual(self.product.discount_percentage, 20.0)

    def test_final_price_property(self):
        """final_price property tekshiruvi"""
        self.assertEqual(self.product.final_price, Decimal("800.00"))

        # Chegirma bo'lmasa
        self.product.discount_price = None
        self.product.save()
        self.assertEqual(self.product.final_price, Decimal("1000.00"))


class ProductImageModelTest(TestCase):
    """ProductImage modeli uchun testlar"""

    def setUp(self):
        seller = CustomUser.objects.create_user(
            username="seller1",
            email="seller@test.com",
            password="test123",
            user_role=SELLER
        )
        category = Category.objects.create(name="Telefonlar")

        self.product = Product.objects.create(
            seller=seller,
            category=category,
            name="Test Phone",
            description="Test",
            price=Decimal("500.00"),
            stock=5
        )

    def test_primary_image_uniqueness(self):
        """Faqat bitta asosiy rasm bo'lishini tekshirish"""
        image1 = ProductImage.objects.create(
            product=self.product,
            is_primary=True
        )
        image2 = ProductImage.objects.create(
            product=self.product,
            is_primary=True
        )

        # Ikkinchi rasm asosiy bo'lganda, birinchisi avtomatik False bo'lishi kerak
        image1.refresh_from_db()
        self.assertFalse(image1.is_primary)
        self.assertTrue(image2.is_primary)


# ============================================
# API/VIEW TESTLARI
# ============================================

class CategoryAPITest(APITestCase):
    """Category API endpoint testlari"""

    def setUp(self):
        self.client = APIClient()
        self.category1 = Category.objects.create(name="Elektronika", is_active=True)
        self.category2 = Category.objects.create(
            name="Telefonlar",
            parent=self.category1,
            is_active=True
        )

    def test_category_list(self):
        """Kategoriyalar ro'yxatini olish"""
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertGreaterEqual(len(response.data['data']), 1)

    def test_category_detail(self):
        """Kategoriya detailini olish"""
        url = reverse('category-detail', kwargs={'slug': self.category1.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['category']['name'], "Elektronika")


class ProductAPITest(APITestCase):
    """Product API endpoint testlari"""

    def setUp(self):
        self.client = APIClient()

        # Userlar yaratish
        self.seller = CustomUser.objects.create_user(
            username="seller1",
            email="seller@test.com",
            password="test123",
            user_role=SELLER
        )
        self.ordinary_user = CustomUser.objects.create_user(
            username="user1",
            email="user@test.com",
            password="test123",
            user_role=ORDINARY_USER
        )

        # Kategoriya va brand
        self.category = Category.objects.create(name="Telefonlar", is_active=True)
        self.brand = Brand.objects.create(name="Samsung", is_active=True)

        # Mahsulot
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            brand=self.brand,
            name="Samsung S24",
            description="Test mahsulot",
            price=Decimal("1000.00"),
            stock=10,
            is_active=True
        )

    def test_product_list_without_auth(self):
        """Ro'yxatdan o'tmagan user mahsulotlarni ko'rishi mumkin"""
        url = reverse('product-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertGreaterEqual(response.data['count'], 1)

    def test_product_detail(self):
        """Mahsulot detailini olish"""
        url = reverse('product-detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], "Samsung S24")

        # views_count oshganini tekshirish
        self.product.refresh_from_db()
        self.assertEqual(self.product.views_count, 1)

    def test_product_create_by_seller(self):
        """Seller mahsulot yarata olishi"""
        self.client.force_authenticate(user=self.seller)

        url = reverse('product-create')
        data = {
            'category': self.category.id,
            'brand': self.brand.id,
            'name': 'Yangi Telefon',
            'description': 'Test',
            'price': '500.00',
            'stock': 5
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(Product.objects.count(), 2)

    def test_product_create_by_ordinary_user_fails(self):
        """Oddiy user mahsulot yarata olmasligi kerak"""
        self.client.force_authenticate(user=self.ordinary_user)

        url = reverse('product-create')
        data = {
            'category': self.category.id,
            'name': 'Test',
            'description': 'Test',
            'price': '500.00',
            'stock': 5
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_update_by_owner(self):
        """Mahsulot egasi o'zgartira olishi"""
        self.client.force_authenticate(user=self.seller)

        url = reverse('product-update', kwargs={'pk': self.product.pk})
        data = {
            'name': 'Samsung S24 Ultra',
            'price': '1200.00',
            'description': 'Yangilangan',
            'category': self.category.id,
            'stock': 15
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Samsung S24 Ultra')

    def test_product_delete_by_owner(self):
        """Mahsulot o'chirish (soft delete)"""
        self.client.force_authenticate(user=self.seller)

        url = reverse('product-delete', kwargs={'pk': self.product.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)

    def test_product_filtering_by_category(self):
        """Kategoriya bo'yicha filter"""
        url = reverse('product-list')
        response = self.client.get(url, {'category': self.category.slug})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_product_filtering_by_price(self):
        """Narx bo'yicha filter"""
        url = reverse('product-list')
        response = self.client.get(url, {'min_price': '500', 'max_price': '1500'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for product in response.data['data']:
            price = Decimal(str(product['price']))
            self.assertGreaterEqual(price, Decimal('500'))
            self.assertLessEqual(price, Decimal('1500'))

    def test_product_search(self):
        """Qidiruv funksiyasi"""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'Samsung'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_product_ordering(self):
        """Tartiblash (ordering)"""
        # Yana bir arzon mahsulot qo'shish
        Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Arzon Telefon",
            description="Test",
            price=Decimal("300.00"),
            stock=5,
            is_active=True
        )

        url = reverse('product-list')
        response = self.client.get(url, {'ordering': 'price'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [Decimal(str(p['price'])) for p in response.data['data']]
        self.assertEqual(prices, sorted(prices))


class BrandAPITest(APITestCase):
    """Brand API testlari"""

    def setUp(self):
        self.client = APIClient()
        self.brand = Brand.objects.create(name="Apple", is_active=True)

    def test_brand_list(self):
        """Brendlar ro'yxati"""
        url = reverse('brand-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_brand_detail(self):
        """Brand detail"""
        url = reverse('brand-detail', kwargs={'slug': self.brand.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['brand']['name'], "Apple")
