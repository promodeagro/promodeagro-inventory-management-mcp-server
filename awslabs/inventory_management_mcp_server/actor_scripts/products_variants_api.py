#!/usr/bin/env python3
"""
Products & Variants API - Your Existing JSON Structure
Simple API to manage products with variants using your existing JSON structure.
Works directly with the Products table - no complex separate tables.
"""

import boto3
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional


class ProductsVariantsAPI:
    """API for managing products with variants using your existing structure"""
    
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.products_table = self.dynamodb.Table('InventoryManagement-Products')
        self.stock_levels_table = self.dynamodb.Table('InventoryManagement-StockLevels')
        self.categories_table = self.dynamodb.Table('InventoryManagement-Categories')
        self.units_table = self.dynamodb.Table('InventoryManagement-ProductUnits')
    
    def create_product_with_variants(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product with variants using your exact JSON structure
        
        Args:
            product_data: Your existing product JSON structure
            
        Returns:
            Dictionary with success status and created product data
        """
        try:
            # Generate groupId if not provided
            if 'groupId' not in product_data:
                product_data['groupId'] = str(uuid.uuid4())
            
            # Prepare the product for DynamoDB
            enhanced_product = {
                # DynamoDB Keys
                'groupId': product_data['groupId'],  # PK
                'category': f"{product_data['category']}#{product_data['subCategory']}",  # SK
                
                # Your existing structure
                'name': product_data['name'],
                'subCategory': product_data['subCategory'],
                'description': product_data.get('description', ''),
                'image': product_data.get('image', ''),
                'images': product_data.get('images', []),
                'tags': product_data.get('tags', []),
                'variations': [],
                
                # Additional fields
                'productType': product_data.get('productType', 'GENERAL'),
                'storageRequirements': product_data.get('storageRequirements', {}),
                'supplier': product_data.get('supplier', {}),
                'inventory': product_data.get('inventory', {}),
                'isActive': product_data.get('isActive', True),
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
            
            # Process variations with Decimal conversion
            for variation in product_data.get('variations', []):
                enhanced_variation = {
                    'id': variation['id'],
                    'name': variation['name'],
                    'unit': variation['unit'],
                    'quantity': variation['quantity'],
                    'mrp': Decimal(str(variation['mrp'])),
                    'price': Decimal(str(variation['price'])),
                    'availability': variation.get('availability', True)
                }
                enhanced_product['variations'].append(enhanced_variation)
            
            # Insert the product
            self.products_table.put_item(Item=enhanced_product)
            
            # Create stock levels for each variant
            self._create_stock_levels_for_variants(enhanced_product)
            
            return {
                'success': True,
                'groupId': enhanced_product['groupId'],
                'message': 'Product created successfully',
                'data': enhanced_product
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create product'
            }
    
    def get_product_by_group_id(self, group_id: str) -> Dict[str, Any]:
        """
        Get a product by its group ID
        
        Args:
            group_id: The product group ID
            
        Returns:
            Dictionary with product data or error
        """
        try:
            # Query by groupId (PK)
            response = self.products_table.query(
                KeyConditionExpression='groupId = :groupId',
                ExpressionAttributeValues={':groupId': group_id}
            )
            
            if response['Items']:
                product = response['Items'][0]
                
                # Get stock levels for variants
                stock_levels = self._get_stock_levels_for_product(group_id)
                product['stockLevels'] = stock_levels
                
                return {
                    'success': True,
                    'data': product
                }
            else:
                return {
                    'success': False,
                    'error': 'Product not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_products_by_category(self, category: str, sub_category: str = None) -> Dict[str, Any]:
        """
        Get all products in a category
        
        Args:
            category: Main category
            sub_category: Optional sub-category filter
            
        Returns:
            Dictionary with list of products
        """
        try:
            if sub_category:
                # Exact category match
                category_key = f"{category}#{sub_category}"
                response = self.products_table.query(
                    IndexName='CategoryIndex',  # Assuming GSI exists
                    KeyConditionExpression='category = :category',
                    ExpressionAttributeValues={':category': category_key}
                )
            else:
                # Scan for category prefix
                response = self.products_table.scan(
                    FilterExpression='begins_with(category, :category)',
                    ExpressionAttributeValues={':category': category}
                )
            
            return {
                'success': True,
                'data': response['Items'],
                'count': len(response['Items'])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_variant_price(self, group_id: str, variant_id: str, new_price: float, new_mrp: float = None) -> Dict[str, Any]:
        """
        Update the price of a specific variant
        
        Args:
            group_id: Product group ID
            variant_id: Specific variant ID
            new_price: New selling price
            new_mrp: New MRP (optional)
            
        Returns:
            Dictionary with success status
        """
        try:
            # Get current product
            product_result = self.get_product_by_group_id(group_id)
            if not product_result['success']:
                return product_result
            
            product = product_result['data']
            
            # Find and update the variant
            variant_updated = False
            for variation in product['variations']:
                if variation['id'] == variant_id:
                    variation['price'] = Decimal(str(new_price))
                    if new_mrp:
                        variation['mrp'] = Decimal(str(new_mrp))
                    variant_updated = True
                    break
            
            if not variant_updated:
                return {
                    'success': False,
                    'error': 'Variant not found'
                }
            
            # Update the product
            product['updatedAt'] = datetime.now(timezone.utc).isoformat()
            
            self.products_table.put_item(Item=product)
            
            return {
                'success': True,
                'message': f'Variant {variant_id} price updated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_variant_availability(self, group_id: str, variant_id: str, availability: bool) -> Dict[str, Any]:
        """
        Update the availability of a specific variant
        
        Args:
            group_id: Product group ID
            variant_id: Specific variant ID
            availability: True/False availability status
            
        Returns:
            Dictionary with success status
        """
        try:
            # Get current product
            product_result = self.get_product_by_group_id(group_id)
            if not product_result['success']:
                return product_result
            
            product = product_result['data']
            
            # Find and update the variant
            variant_updated = False
            for variation in product['variations']:
                if variation['id'] == variant_id:
                    variation['availability'] = availability
                    variant_updated = True
                    break
            
            if not variant_updated:
                return {
                    'success': False,
                    'error': 'Variant not found'
                }
            
            # Update the product
            product['updatedAt'] = datetime.now(timezone.utc).isoformat()
            
            self.products_table.put_item(Item=product)
            
            return {
                'success': True,
                'message': f'Variant {variant_id} availability updated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_stock_levels(self, group_id: str, variant_id: str = None) -> Dict[str, Any]:
        """
        Get stock levels for a product or specific variant
        
        Args:
            group_id: Product group ID
            variant_id: Optional specific variant ID
            
        Returns:
            Dictionary with stock level data
        """
        try:
            if variant_id:
                # Get stock for specific variant
                response = self.stock_levels_table.query(
                    KeyConditionExpression='productId = :productId AND begins_with(#loc, :variantPrefix)',
                    ExpressionAttributeNames={'#loc': 'location'},
                    ExpressionAttributeValues={
                        ':productId': group_id,
                        ':variantPrefix': f'WAREHOUSE-HYDERABAD-01#{variant_id}'
                    }
                )
            else:
                # Get stock for all variants
                response = self.stock_levels_table.query(
                    KeyConditionExpression='productId = :productId',
                    ExpressionAttributeValues={':productId': group_id}
                )
            
            return {
                'success': True,
                'data': response['Items']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_stock_level(self, group_id: str, variant_id: str, stock_change: int, location: str = 'WAREHOUSE-HYDERABAD-01') -> Dict[str, Any]:
        """
        Update stock level for a specific variant
        
        Args:
            group_id: Product group ID
            variant_id: Specific variant ID
            stock_change: Change in stock (positive or negative)
            location: Warehouse location
            
        Returns:
            Dictionary with success status
        """
        try:
            stock_key = f"{location}#{variant_id}"
            
            # Update stock level
            response = self.stock_levels_table.update_item(
                Key={
                    'productId': group_id,
                    'location': stock_key
                },
                UpdateExpression='SET availableStock = availableStock + :change, totalStock = totalStock + :change, lastUpdated = :timestamp',
                ExpressionAttributeValues={
                    ':change': stock_change,
                    ':timestamp': datetime.now(timezone.utc).isoformat()
                },
                ReturnValues='ALL_NEW'
            )
            
            return {
                'success': True,
                'message': f'Stock updated by {stock_change}',
                'data': response['Attributes']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_products(self, search_term: str) -> Dict[str, Any]:
        """
        Search products by name or tags
        
        Args:
            search_term: Search term
            
        Returns:
            Dictionary with matching products
        """
        try:
            # Simple scan with filter (for production, use ElasticSearch or similar)
            response = self.products_table.scan(
                FilterExpression='contains(#name, :term) OR contains(tags, :term)',
                ExpressionAttributeNames={'#name': 'name'},
                ExpressionAttributeValues={':term': search_term}
            )
            
            return {
                'success': True,
                'data': response['Items'],
                'count': len(response['Items'])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_stock_levels_for_variants(self, product: Dict[str, Any]):
        """Create initial stock level entries for all variants"""
        try:
            for variation in product['variations']:
                stock_entry = {
                    'productId': product['groupId'],  # PK
                    'location': f'WAREHOUSE-HYDERABAD-01#{variation["id"]}',  # SK
                    'groupId': product['groupId'],
                    'variantId': variation['id'],
                    'variantName': variation['name'],
                    'unit': variation['unit'],
                    'quantity': variation['quantity'],
                    'totalStock': 0,  # Will be updated when stock arrives
                    'availableStock': 0,
                    'reservedStock': 0,
                    'damagedStock': 0,
                    'expiredStock': 0,
                    'reorderPoint': 20,
                    'maxStock': 500,
                    'lastRestocked': datetime.now(timezone.utc).isoformat(),
                    'lastUpdated': datetime.now(timezone.utc).isoformat()
                }
                
                self.stock_levels_table.put_item(Item=stock_entry)
                
        except Exception as e:
            print(f"Warning: Could not create stock levels: {str(e)}")
    
    def _get_stock_levels_for_product(self, group_id: str) -> List[Dict[str, Any]]:
        """Get stock levels for all variants of a product"""
        try:
            response = self.stock_levels_table.query(
                KeyConditionExpression='productId = :productId',
                ExpressionAttributeValues={':productId': group_id}
            )
            return response['Items']
        except Exception as e:
            print(f"Warning: Could not get stock levels: {str(e)}")
            return []


# Example usage and testing
def example_usage():
    """Example of how to use the ProductsVariantsAPI"""
    
    api = ProductsVariantsAPI()
    
    # Your existing product data structure
    your_product = {
        "groupId": "8b7bb419-f868-491c-bba6-7785e78b62cf",
        "name": "Bharta Brinjal (Black medium pieces)",
        "category": "Bengali Special",
        "subCategory": "Bengali Vegetables",
        "description": "Bharta Brinjal (Begun) is a special variety of large, fleshy eggplant...",
        "image": "https://cdn.example.com/image1.webp",
        "images": [
            "https://cdn.example.com/image1.webp",
            "",
            ""
        ],
        "tags": [
            "bharta brinjal", "begun", "baingan", "roasting eggplant"
        ],
        "variations": [
            {
                "id": "9381385120",
                "name": "Bharta Brinjal (1 Kg)",
                "unit": "Kg",
                "quantity": 1,
                "mrp": 120,
                "price": 90,
                "availability": True
            },
            {
                "id": "9271560014",
                "name": "Bharta Brinjal (500 Gms)",
                "unit": "Gms",
                "quantity": 500,
                "mrp": 60,
                "price": 45,
                "availability": True
            },
            {
                "id": "8628945059",
                "name": "Bharta Brinjal (250 Gms)",
                "unit": "Gms",
                "quantity": 250,
                "mrp": 30,
                "price": 23,
                "availability": True
            }
        ]
    }
    
    # Create the product
    result = api.create_product_with_variants(your_product)
    print(f"Create result: {result}")
    
    # Get the product
    product = api.get_product_by_group_id("8b7bb419-f868-491c-bba6-7785e78b62cf")
    print(f"Get result: {product}")
    
    # Update variant price
    price_update = api.update_variant_price(
        "8b7bb419-f868-491c-bba6-7785e78b62cf",
        "9381385120",
        95.00,  # New price
        125.00  # New MRP
    )
    print(f"Price update result: {price_update}")
    
    # Get products by category
    category_products = api.get_products_by_category("Bengali Special", "Bengali Vegetables")
    print(f"Category products: {category_products}")
    
    # Update stock level
    stock_update = api.update_stock_level(
        "8b7bb419-f868-491c-bba6-7785e78b62cf",
        "9381385120",
        50  # Add 50 units
    )
    print(f"Stock update result: {stock_update}")
    
    # Search products
    search_result = api.search_products("brinjal")
    print(f"Search result: {search_result}")


if __name__ == '__main__':
    example_usage()
