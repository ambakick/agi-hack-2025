#!/usr/bin/env python3
"""
Test script for Google Cloud Text-to-Speech integration.
Run this after updating your .env file with GOOGLE_TTS_API_KEY.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.google_tts import GoogleTTSService
from app.models.schemas import ScriptResponse, ScriptSegment, PodcastFormat
from app.core.config import settings


async def test_single_host():
    """Test single-host audio generation."""
    print("\n=== Testing Single-Host TTS ===")
    
    service = GoogleTTSService(api_key=settings.google_tts_api_key)
    
    # Create a simple script
    script = ScriptResponse(
        format=PodcastFormat.SINGLE_HOST,
        full_script="Hello! This is a test of Google Cloud Text-to-Speech. The Neural2 voices sound quite natural, don't they?",
        segments=[]
    )
    
    print("Generating audio...")
    audio_data = await service.generate_audio(script)
    
    # Save to file
    output_file = Path("test_single_host.mp3")
    with open(output_file, "wb") as f:
        f.write(audio_data)
    
    print(f"✓ Single-host audio generated: {output_file} ({len(audio_data)} bytes)")
    return True


async def test_multi_host():
    """Test multi-host audio generation."""
    print("\n=== Testing Multi-Host TTS ===")
    
    service = GoogleTTSService(api_key=settings.google_tts_api_key)
    
    # Create a multi-host script
    segments = [
        ScriptSegment(speaker="HOST_1", text="Welcome to our podcast! I'm your host, Sarah."),
        ScriptSegment(speaker="HOST_2", text="And I'm John. Today we're testing Google's Text-to-Speech."),
        ScriptSegment(speaker="HOST_1", text="The Neural2 voices are really impressive!"),
        ScriptSegment(speaker="HOST_2", text="Absolutely! They sound very natural and engaging."),
    ]
    
    script = ScriptResponse(
        format=PodcastFormat.TWO_HOSTS,
        full_script="",  # Not used in multi-host
        segments=segments
    )
    
    print(f"Generating audio with {len(segments)} segments...")
    audio_data = await service.generate_audio(script)
    
    # Save to file
    output_file = Path("test_multi_host.mp3")
    with open(output_file, "wb") as f:
        f.write(audio_data)
    
    print(f"✓ Multi-host audio generated: {output_file} ({len(audio_data)} bytes)")
    return True


async def test_voice_list():
    """Test listing available voices."""
    print("\n=== Testing Voice List ===")
    
    service = GoogleTTSService(api_key=settings.google_tts_api_key)
    
    print("Fetching available Neural2 voices...")
    voices = await service.get_available_voices()
    
    print(f"✓ Found {len(voices)} Neural2 voices:")
    for voice in voices[:5]:  # Show first 5
        print(f"  - {voice['name']} ({voice['ssml_gender']})")
    
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Google Cloud Text-to-Speech Integration Test")
    print("=" * 60)
    
    try:
        # Test voice listing
        await test_voice_list()
        
        # Test single-host generation
        await test_single_host()
        
        # Test multi-host generation
        await test_multi_host()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - test_single_host.mp3")
        print("  - test_multi_host.mp3")
        print("\nYou can play these files to verify audio quality.")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Test failed: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
