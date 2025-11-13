"""
Maritime Container Extensions for py3dbp
Adds container ship specific attributes and constraints
"""
from py3dbp.main import Item


class MaritimeContainer(Item):
    """
    Extended Item class for maritime containers with cargo-specific attributes
    """
    def __init__(self, container_id, teu_size, cargo_type, total_weight,
                 dimensions, empty_weight=None, destination='PORT_B',
                 hazmat_class=None, loading_priority=1, **kwargs):
        """
        Args:
            container_id: Unique container identifier
            teu_size: '20ft' or '40ft'
            cargo_type: 'general', 'reefer', or 'hazmat'
            total_weight: Total weight including container + cargo (tonnes)
            dimensions: (length, width, height) in meters
            empty_weight: Container tare weight (tonnes)
            destination: Destination port
            hazmat_class: If hazmat, specify class (e.g., 'Class_3')
            loading_priority: 1=high, 5=low
        """
        # Initialize parent Item class
        super().__init__(
            partno=container_id,
            name=cargo_type,
            typeof='cube',  # Containers are rectangular
            WHD=dimensions,
            weight=total_weight,
            level=loading_priority,  # py3dbp priority
            loadbear=100,  # Default load bearing
            updown=False,  # Containers don't flip
            color=self._get_color_by_type(cargo_type)
        )
        
        # Maritime-specific attributes
        self.container_id = container_id
        self.teu_size = teu_size
        self.teu_value = 1 if teu_size == '20ft' else 2
        self.cargo_type = cargo_type
        self.total_weight = total_weight
        self.empty_weight = empty_weight or (2.3 if teu_size == '20ft' else 3.75)
        self.cargo_weight = total_weight - self.empty_weight
        self.destination = destination
        self.hazmat_class = hazmat_class
        self.loading_priority = loading_priority
        
        # Will be set during packing
        self.assigned_slot = None
        self.bay = None
        self.row = None
        self.tier = None
    
    @staticmethod
    def _get_color_by_type(cargo_type):
        """Assign colors based on cargo type for visualization"""
        colors = {
            'general': 'blue',
            'reefer': 'cyan',
            'hazmat': 'red'
        }
        return colors.get(cargo_type, 'gray')
    
    def is_hazmat(self):
        """Check if container contains hazardous materials"""
        return self.cargo_type == 'hazmat'
    
    def is_reefer(self):
        """Check if container requires refrigeration"""
        return self.cargo_type == 'reefer'
    
    def __repr__(self):
        return f"MaritimeContainer({self.container_id}, {self.teu_size}, {self.cargo_type}, {self.total_weight}t)"