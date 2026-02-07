<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <html>
      <head><link rel="stylesheet" type="text/css" href="style.css"/></head>
      <body>
        <div class="dashboard-wrapper">
          <h1>Global Maritime Chokepoint Risk Dashboard</h1>
          
          <header class="summary-section">
            <h2>Global Maritime Summary</h2>
            <p><strong>Global risk index:</strong> <xsl:value-of select="dashboard/global_summary/index_score"/> (<xsl:value-of select="dashboard/global_summary/risk_label"/>)</p>
            <p><xsl:value-of select="dashboard/global_summary/description"/></p>
            <p>Highest operational risk: <xsl:value-of select="dashboard/global_summary/highest_risk_point"/></p>
            <p>Risk distribution: 
               <xsl:value-of select="count(//status[@label='LOW'])"/> low, 
               <xsl:value-of select="count(//status[@label='MODERATE'])"/> moderate, 
               <xsl:value-of select="count(//status[@label='HIGH'])"/> high.
            </p>
          </header>

          <xsl:for-each select="dashboard/chokepoints/point">
            <section class="chokepoint-card">
              <h3><xsl:value-of select="@name"/></h3>
              <p class="summary-line">Summary: <xsl:value-of select="current/@temp"/>°C, <xsl:value-of select="current/@wind"/> km/h wind...</p>
              
              <div class="risk-badge">
                <xsl:attribute name="class">risk-badge <xsl:value-of select="status/@label"/></xsl:attribute>
                <xsl:value-of select="status/@label"/> (Score: <xsl:value-of select="status/@score"/>)
              </div>

              <div class="details">
                <p><strong>Transit difficulty index:</strong> <xsl:value-of select="status/@difficulty"/> (<xsl:value-of select="status/@difficulty_label"/>)</p>
                <p><strong>Outlook:</strong> <xsl:value-of select="outlook"/></p>
                <p><strong>Operational Impact:</strong> <xsl:value-of select="impact"/></p>
              </div>

              <h4>24-Hour Forecast</h4>
              <table class="forecast-table">
                <tr><th>Time</th><th>Temp</th><th>Wind</th><th>Vis</th><th>Precip</th></tr>
                <xsl:for-each select="forecast/hour">
                  <tr>
                    <td><xsl:value-of select="substring(@time, 12, 5)"/></td>
                    <td><xsl:value-of select="@temp"/>°C</td>
                    <td><xsl:value-of select="@wind"/> km/h</td>
                    <td><xsl:value-of select="@vis"/> m</td>
                    <td><xsl:value-of select="@precip"/> mm</td>
                  </tr>
                </xsl:for-each>
              </table>
            </section>
          </xsl:for-each>
          
          <footer>© 2026 Randy Hinton. For situational awareness only.</footer>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
