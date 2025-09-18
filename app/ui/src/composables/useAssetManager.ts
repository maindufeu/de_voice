import type { AssetRefs, UIMessage } from '../types/chat';
import { apiService } from '../services/apiService';

/**
 * Composable for managing asset loading
 * @param updateMessage Function to update a message with new content
 */
export function useAssetManager(updateMessage: (index: number, updates: Partial<UIMessage>) => void) {
  
  /**
   * Load assets based on references and update the message
   * @param assetRefs Asset references (image_ids, data_id)
   * @param messageIndex Index of the message to update with loaded assets
   */
  const loadAssetsFromRefs = async (assetRefs: AssetRefs, messageIndex: number): Promise<void> => {
    try {
      // Set loading flag
      updateMessage(messageIndex, { assetsLoading: true });
      
      // Load images if there are any image IDs
      if (assetRefs.image_ids && assetRefs.image_ids.length > 0) {
        const imagePromises = assetRefs.image_ids.map(imageId => apiService.loadImageAsset(imageId));
        
        // Wait for all image promises to resolve
        const images = await Promise.all(imagePromises);
        // Filter out null values (failed loads)
        const validImages = images.filter(img => img !== null) as string[];
        
        // Update the message with the loaded images
        if (validImages.length > 0) {
          updateMessage(messageIndex, { images: validImages });
        }
      }
      
      // Load data if there's a data ID
      if (assetRefs.data_id) {
        try {
          const data = await apiService.loadDataAsset(assetRefs.data_id);
          
          // Update the message with the loaded data
          if (data) {
            updateMessage(messageIndex, { data });
          }
        } catch (err) {
          console.error(`Error loading data ${assetRefs.data_id}:`, err);
        }
      }
      
      // Clear loading flag
      updateMessage(messageIndex, { assetsLoading: false });
    } catch (err) {
      console.error('Error loading assets:', err);
      // Ensure loading flag is cleared even on error
      updateMessage(messageIndex, { assetsLoading: false });
    }
  };
  
  return {
    loadAssetsFromRefs
  };
}