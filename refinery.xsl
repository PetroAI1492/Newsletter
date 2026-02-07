<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <html>
      <head>
        <link rel="stylesheet" type="text/css" href="style.css"/>
      </head>
      <body>
        <div class="container">
          <header>
            <h1><xsl:value-of select="newsletter/metadata/title"/></h1>
            <p class="date">Intel Date: <xsl:value-of select="newsletter/metadata/date"/></p>
            <div class="alert-box">
               WARNING: <xsl:value-of select="newsletter/metadata/status"/>
            </div>
          </header>

          <section class="overview">
            <h3>Executive Overview</h3>
            <p><xsl:value-of select="newsletter/executive_overview"/></p>
          </section>

          <section class="data-grid">
            <xsl:for-each select="newsletter/market_impacts/stat">
              <div class="stat-card">
                <span class="label"><xsl:value-of select="@label"/></span>
                <span class="value"><xsl:value-of select="."/></span>
              </div>
            </xsl:for-each>
          </section>

          <section class="geopolitics">
            <h3>Current Developments</h3>
            <ul>
              <xsl:for-each select="newsletter/geopolitics/event">
                <li><strong><xsl:value-of select="@title"/>:</strong> <xsl:value-of select="."/></li>
              </xsl:for-each>
            </ul>
          </section>

          <footer>
            Professional Energy Newsletter | © 2026 PetroAI1492 Energy Empire
          </footer>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
