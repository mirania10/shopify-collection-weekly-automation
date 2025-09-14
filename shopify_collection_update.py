#!/usr/bin/env python3
"""
Shopify Collection Weekly Automation Script

This script automatically fetches new Shopify products added within the last week,
clears existing manual collections, and updates them with fresh products.

Author: Automated Collection Management
Version: 1.0
Date: September 2025
"""

import requests
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('shopify_automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ShopifyCollectionAutomation:
    """
    A class to handle automated Shopify collection management.
    """
    
    def __init__(self):
        """Initialize the automation with Shopify API credentials."""
        self.api_key = os.getenv('SHOPIFY_API_KEY')
        self.password = os.getenv('SHOPIFY_PASSWORD')
        self.shop_name = os.getenv('SHOPIFY_SHOP_NAME')
        self.collection_id = os.getenv('COLLECTION_ID')
        
        if not all([self.api_key, self.password, self.shop_name, self.collection_id]):
            raise ValueError("Missing required environment variables. Please check your .env file.")
        
        self.base_url = f"https://{self.shop_name}.myshopify.com/admin/api/2023-10"
        self.auth = (self.api_key, self.password)
        
        logger.info(f"Initialized Shopify automation for shop: {self.shop_name}")
    
    def get_new_products(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch products created within the specified number of days.
        
        Args:
            days_back (int): Number of days to look back for new products
            
        Returns:
            List[Dict[str, Any]]: List of product dictionaries
        """
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        url = f"{self.base_url}/products.json"
        params = {
            'created_at_min': cutoff_date,
            'limit': 250,  # Maximum allowed by Shopify API
            'status': 'active'
        }
        
        try:
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            
            products_data = response.json()
            products = products_data.get('products', [])
            
            logger.info(f"Found {len(products)} new products from the last {days_back} days")
            return products
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching new products: {e}")
            return []
    
    def get_collection_products(self, collection_id: str) -> List[Dict[str, Any]]:
        """
        Get all products currently in a collection.
        
        Args:
            collection_id (str): The collection ID
            
        Returns:
            List[Dict[str, Any]]: List of products in the collection
        """
        url = f"{self.base_url}/collections/{collection_id}/products.json"
        
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            
            products_data = response.json()
            products = products_data.get('products', [])
            
            logger.info(f"Found {len(products)} products in collection {collection_id}")
            return products
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching collection products: {e}")
            return []
    
    def clear_collection(self, collection_id: str) -> bool:
        """
        Remove all products from a manual collection.
        
        Args:
            collection_id (str): The collection ID to clear
            
        Returns:
            bool: True if successful, False otherwise
        """
        current_products = self.get_collection_products(collection_id)
        
        if not current_products:
            logger.info(f"Collection {collection_id} is already empty")
            return True
        
        success_count = 0
        for product in current_products:
            if self.remove_product_from_collection(collection_id, product['id']):
                success_count += 1
        
        logger.info(f"Removed {success_count}/{len(current_products)} products from collection")
        return success_count == len(current_products)
    
    def remove_product_from_collection(self, collection_id: str, product_id: int) -> bool:
        """
        Remove a specific product from a collection.
        
        Args:
            collection_id (str): The collection ID
            product_id (int): The product ID to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/collections/{collection_id}/products/{product_id}.json"
        
        try:
            response = requests.delete(url, auth=self.auth)
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error removing product {product_id} from collection: {e}")
            return False
    
    def add_products_to_collection(self, collection_id: str, product_ids: List[int]) -> int:
        """
        Add multiple products to a collection.
        
        Args:
            collection_id (str): The collection ID
            product_ids (List[int]): List of product IDs to add
            
        Returns:
            int: Number of products successfully added
        """
        success_count = 0
        
        for product_id in product_ids:
            if self.add_product_to_collection(collection_id, product_id):
                success_count += 1
        
        logger.info(f"Added {success_count}/{len(product_ids)} products to collection")
        return success_count
    
    def add_product_to_collection(self, collection_id: str, product_id: int) -> bool:
        """
        Add a single product to a collection.
        
        Args:
            collection_id (str): The collection ID
            product_id (int): The product ID to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/collections/{collection_id}/products.json"
        
        data = {
            "product": {
                "id": product_id
            }
        }
        
        try:
            response = requests.post(url, auth=self.auth, json=data)
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error adding product {product_id} to collection: {e}")
            return False
    
    def get_collection_info(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific collection.
        
        Args:
            collection_id (str): The collection ID
            
        Returns:
            Optional[Dict[str, Any]]: Collection information or None if error
        """
        url = f"{self.base_url}/collections/{collection_id}.json"
        
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            
            collection_data = response.json()
            return collection_data.get('collection')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching collection info: {e}")
            return None
    
    def run_weekly_update(self) -> Dict[str, Any]:
        """
        Execute the complete weekly collection update process.
        
        Returns:
            Dict[str, Any]: Summary of the update process
        """
        logger.info("Starting weekly collection update process")
        
        # Get collection information
        collection_info = self.get_collection_info(self.collection_id)
        if not collection_info:
            return {
                'success': False,
                'error': 'Could not fetch collection information',
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info(f"Updating collection: {collection_info.get('title', 'Unknown')}")
        
        # Get new products from the last week
        new_products = self.get_new_products(days_back=7)
        
        if not new_products:
            logger.info("No new products found from the last week")
            return {
                'success': True,
                'products_found': 0,
                'products_added': 0,
                'message': 'No new products to add',
                'timestamp': datetime.now().isoformat()
            }
        
        # Clear existing collection
        logger.info(f"Clearing existing products from collection {self.collection_id}")
        clear_success = self.clear_collection(self.collection_id)
        
        if not clear_success:
            logger.warning("Some products could not be removed from collection")
        
        # Add new products to collection
        product_ids = [product['id'] for product in new_products]
        added_count = self.add_products_to_collection(self.collection_id, product_ids)
        
        summary = {
            'success': True,
            'collection_name': collection_info.get('title', 'Unknown'),
            'products_found': len(new_products),
            'products_added': added_count,
            'collection_cleared': clear_success,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Weekly update completed: {summary}")
        return summary

def main():
    """
    Main function to run the automation script.
    """
    try:
        # Initialize the automation
        automation = ShopifyCollectionAutomation()
        
        # Run the weekly update
        result = automation.run_weekly_update()
        
        # Print results
        print("\n" + "="*50)
        print("SHOPIFY COLLECTION AUTOMATION SUMMARY")
        print("="*50)
        print(f"Collection: {result.get('collection_name', 'Unknown')}")
        print(f"Products Found: {result.get('products_found', 0)}")
        print(f"Products Added: {result.get('products_added', 0)}")
        print(f"Collection Cleared: {result.get('collection_cleared', False)}")
        print(f"Status: {'SUCCESS' if result.get('success') else 'FAILED'}")
        print(f"Timestamp: {result.get('timestamp', 'Unknown')}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        
        print("="*50)
        
        # Return appropriate exit code
        return 0 if result.get('success') else 1
        
    except Exception as e:
        logger.error(f"Automation failed with error: {e}")
        print(f"\nERROR: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
