// Utility functions for fetching data from JSON files
import type {
  WeatherData,
  OuraMetrics,
  MoodData,
  DeveloperStats,
  LocationData,
  SoundCloudTrack,
  ThemeConfig,
  Achievement,
  AIIdentity,
} from '../types';

const BASE_PATH = import.meta.env.BASE_URL;

export async function fetchData<T>(path: string): Promise<T | null> {
  try {
    // Remove leading slash from path if present
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    // Ensure BASE_PATH ends with / before concatenating
    const basePath = BASE_PATH.endsWith('/') ? BASE_PATH : `${BASE_PATH}/`;
    const url = `${basePath}${cleanPath}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      console.warn(`Failed to fetch ${url}: ${response.status}`);
      return null;
    }
    return await response.json() as T;
  } catch (error) {
    console.error(`Error fetching ${path}:`, error);
    return null;
  }
}

export async function fetchAllData() {
  const [
    weather,
    oura,
    mood,
    developer,
    location,
    soundcloud,
    theme,
    achievements,
    aiIdentity
  ] = await Promise.all([
    fetchData<WeatherData>('weather/weather.json'),
    fetchData<OuraMetrics>('oura/metrics.json'),
    fetchData<MoodData>('oura/mood.json'),
    fetchData<DeveloperStats>('developer/stats.json'),
    fetchData<LocationData>('location/location.json'),
    fetchData<SoundCloudTrack>('soundcloud/latest.json'),
    fetchData<ThemeConfig>('config/theme.json'),
    fetchData<Achievement[]>('achievements/achievements.json'),
    fetchData<AIIdentity>('ai/identity.json'),
  ]);

  return {
    weather,
    oura,
    mood,
    developer,
    location,
    soundcloud,
    theme,
    achievements,
    aiIdentity,
  };
}
