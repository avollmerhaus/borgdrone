workflow:

VM an pathfinder der LXC oder kvm class übergeben
	prüft ob vm vorhanden
		returned liste der pfade

liste der geräte an snapshotCreate funktion übergeben
	fährt VM runter
		snapshot jedes elements
		start VM
		returned liste der snapshots

liste der snapshots an copySource2Target
	btrfs rotieren
	rsync oder raw bytes klonen
	

liste der snapshots an snapshotRemove funktion übergeben

btrfs dedup
