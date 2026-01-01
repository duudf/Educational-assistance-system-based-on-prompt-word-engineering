import defaultSettings from '@/settings'

const title = defaultSettings.title || '基于提示词工程的教辅系统'

export default function getPageTitle(pageTitle) {
  if (pageTitle) {
    return `${pageTitle} - ${title}`
  }
  return `${title}`
}
